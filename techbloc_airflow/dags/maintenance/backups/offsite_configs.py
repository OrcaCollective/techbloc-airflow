from dataclasses import dataclass, field
from textwrap import dedent


@dataclass
class OffsiteConfig:
    name: str
    folder: str
    volume: str
    backup_folder: str = "~/backups"

    filename: str = field(init=False)
    final_path: str = field(init=False)
    command: str = field(init=False)

    def __post_init__(self):
        self.filename = f"{self.name}-backup.tar.bz2"
        self.final_path = f"{self.backup_folder}/{self.filename}"
        self.command = dedent(f"""
        cd {self.folder} && \
        just down && \
        docker run --rm \
            -v {self.volume}:/volume \
            -v {self.backup_folder}:/backup \
            loomchild/volume-backup \
            backup {self.filename} && \
        just up
        """)


OFFSITE_CONFIGS = [
    OffsiteConfig(
        name="matrix",
        folder="synapse",
        volume="synapse_synapse_pg_data",
    ),
    OffsiteConfig(
        name="openoversight",
        folder="OpenOversight",
        volume="openoversight_postgres",
    ),
]
