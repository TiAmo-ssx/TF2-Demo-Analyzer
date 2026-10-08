import hashlib
from pathlib import Path


class HashManager:
    """
    DEM 文件 SHA-256 计算器。

    负责：
        DEM 文件
          ↓
        SHA-256
          ↓
        hexdigest

    同一个 DEM 文件（即使文件名不同）
    会得到相同的 hash，用于去重。
    """

    def calculate(
        self,
        file_path,
        chunk_size=1024 * 1024
    ):
        """
        计算文件 SHA-256。

        参数：
            file_path:
                文件路径

            chunk_size:
                分块读取大小（默认 1MB）

        返回：
            str
                64 位十六进制 hash
        """

        file_path = Path(file_path)

        sha256 = hashlib.sha256()

        with open(
            file_path,
            "rb"
        ) as f:

            while True:

                chunk = f.read(
                    chunk_size
                )

                if not chunk:
                    break

                sha256.update(
                    chunk
                )

        return sha256.hexdigest()
