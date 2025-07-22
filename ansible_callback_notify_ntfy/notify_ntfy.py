# notify_ntfy.py
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import os
from datetime import datetime
from ansible.plugins.callback import CallbackBase
import requests

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'notify_ntfy'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()
        # Starttime per Task-UUID
        self.task_start_times = {}
        # Results with dicts: host, task_name, duration, skipped, failed, unreachable
        self.task_results = []
        self.start_time = None
        self.end_time = None
        self.ntfy_url = os.getenv("NTFY_URL", "https://ntfy.example.com/ansible")
        self.ntfy_user = os.getenv("NTFY_USER")
        self.ntfy_pass = os.getenv("NTFY_PASS")

    def v2_playbook_on_start(self, playbook):
        self.start_time = datetime.now()

    def v2_playbook_on_task_start(self, task, is_conditional):
        """Remember the starttime per Task (global, for all hosts)"""
        task_uuid = task._uuid
        self.task_start_times[task_uuid] = datetime.now()

    def _record_task_result(self, result, skipped=False, failed=False, unreachable=False):
        host = result._host.get_name()
        task_name = result.task_name or "unknown task"
        task_uuid = result._task._uuid if hasattr(result, '_task') else None

        duration = None
        if task_uuid and task_uuid in self.task_start_times:
            start = self.task_start_times[task_uuid]
            duration = (datetime.now() - start).total_seconds()

        if duration is None:
            duration = 0.0

        self.task_results.append({
            'host': host,
            'task': task_name,
            'duration': duration,
            'skipped': skipped,
            'failed': failed,
            'unreachable': unreachable,
        })

    def v2_runner_on_ok(self, result):
        self._record_task_result(result, skipped=False, failed=False)

    def v2_runner_on_skipped(self, result):
        self._record_task_result(result, skipped=True, failed=False)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._record_task_result(result, skipped=False, failed=True)

    def v2_runner_on_unreachable(self, result):
        host = result._host.get_name()
        task_name = result.task_name or "unreachable"
        task_uuid = result._task._uuid if hasattr(result, '_task') else None

        duration = None
        if task_uuid and task_uuid in self.task_start_times:
            start = self.task_start_times[task_uuid]
            duration = (datetime.now() - start).total_seconds()

        if duration is None:
            duration = 0.0

        self.task_results.append({
            'host': host,
            'task': task_name,
            'duration': duration,
            'skipped': False,
            'failed': True,
            'unreachable': True,
        })

    def v2_playbook_on_stats(self, stats):
        self.end_time = datetime.now()
        total_time = self.end_time - self.start_time if self.start_time else None

        recap_msgs = []
        hosts = sorted(stats.processed.keys())

        recap_msgs.append("PLAYBOOK RECAP")
        for host in hosts:
            s = stats.summarize(host)
            recap_msgs.append(
                f"{host} : ok={s['ok']} changed={s['changed']} unreachable={s['unreachable']} failed={s['failures']} "
                f"skipped={s['skipped']} rescued={s['rescued']} ignored={s['ignored']}"
            )

        if total_time:
            recap_msgs.append("")
            recap_msgs.append(f"Playbook run took {str(total_time)}")

        recap_msgs.append("")
        recap_msgs.append("TASKS RECAP")

        # Sort after duration, descending
        self.task_results.sort(
            key=lambda x: x['duration'] if x['duration'] is not None else 0.0, reverse=True
        )

        for t in self.task_results:
            dur_str = f"{t['duration']:.2f}s" if t['duration'] is not None else "n/a"
            skip_str = " (skipped)" if t['skipped'] else ""
            fail_str = ""
            if t.get('failed'):
                fail_str = " (failed)"
            if t.get('unreachable'):
                fail_str = " (unreachable)"
            recap_msgs.append(f"{t['host']} : {t['task']} - {dur_str}{skip_str}{fail_str}")

        message = "\n".join(recap_msgs)
        self._send_ntfy(message)

    def _send_ntfy(self, message):
        headers = {
            'Title': 'Ansible Playbook Recap',
            'Priority': '5',
            'Tags': 'ansible,recap',
        }
        auth = None
        if self.ntfy_user and self.ntfy_pass:
            auth = (self.ntfy_user, self.ntfy_pass)
        try:
            r = requests.post(
                self.ntfy_url, data=message.encode('utf-8'), headers=headers, auth=auth, timeout=10
            )
            if 200 <= r.status_code < 300:
                self._display.banner("Sent recap notification to ntfy")
            else:
                self._display.warning(f"Failed to send ntfy notification, status {r.status_code}: {r.text}")
        except Exception as e:
            self._display.warning(f"Exception sending ntfy notification: {e}")
