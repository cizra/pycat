import os

from modules.basemodule import BaseModule


class FileEdit(BaseModule):
    """
    Use your mud client's builtin editor to modify files.

    This is only really useful if pycat isn't running on the same machine as your client.
    """
    open_file = None

    def alias(self, line: str) -> bool:
        if self.open_file is not None:
            if line == '.':
                self.open_file.close()
                self.open_file = None
            else:
                self.open_file.write(line + '\n')
            return True
        elif line.startswith("#edit "):
            self.send_file(line[6:])
            return True
        elif line.startswith('#write-file '):
            self.write_file(line[12:])
            return True
        return False

    def send_file(self, file: str) -> None:
        msg = f"#$# edit name: {file} upload: #write-file {file}"
        if os.path.exists(file):
            with open(file) as f:
                for line in f.readlines():
                    msg += '\n' + line
        else:
            msg += '\n% Warning:  Creating new file.'
        msg = msg.strip()  # Trim trailing newline
        msg += '\n.'
        self.log(msg, bar=False)

    def write_file(self, file: str) -> None:
        self.open_file = open(file, 'w')
