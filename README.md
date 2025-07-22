# ansible_callback_notify_ntfy

An Ansible Callback Plugin that sends playbook and task recaps to an NTFY server at the end of a run.

## Installation

### Option 1: Manual Integration

- Copy the `notify_ntfy.py` plugin file into your Ansible project under a directory like `.plugins/callback/notify_ntfy.py`.
- Enable the plugin in your `ansible.cfg`:

```ini
[defaults]
callback_plugins = .plugins/callback
callbacks_enabled = notify_ntfy
```

### Option 2: Install via pip

You can install the plugin directly from GitHub:

```shell
pip install git+https://github.com/madic-creates/ansible_callback_notify_ntfy.git
```

Then make sure to add the installed plugin path to your `ansible.cfg`:

```ini
[defaults]
callback_plugins = /path/to/python/site-packages/ansible_callback_notify_ntfy/
callbacks_enabled = notify_ntfy
```

(Use `python -m site` to locate your site-packages directory.)

## Configuration

Set these environment variables before running your playbook:

```shell
export NTFY_URL=https://ntfy.example.com/your-topic
export NTFY_USER=yourusername     # optional
export NTFY_PASS=yourpassword     # optional
```

- `NTFY_URL`: The URL of your NTFY server endpoint (topic URL).
- `NTFY_USER` and `NTFY_PASS`: Optional basic authentication credentials if your NTFY server requires authentication.

## Usage

Run your playbooks as usual. At the end of each playbook run, a notification with the playbook and task recap will be sent to the configured NTFY topic.

## Features

- Sends playbook recap including host-level statistics (ok, changed, failed, unreachable, skipped).
- Includes detailed task recap sorted by duration (descending).
- Marks skipped, failed, and unreachable tasks distinctly.
- Supports basic authentication for secured NTFY endpoints.

## License

MIT License - see LICENSE file for details.

## Contributing

Feel free to submit issues and pull requests.

## Contact

For questions or support, open an issue in the GitHub repository.
