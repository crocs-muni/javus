from jsec.executor import BaseAttackExecutor
from jsec.builder import BaseBuilder
import random
import subprocess
import random
import pyradamsa
from jsec.utils import cd, proc_to_dict
from jsec.settings import SUBMODULES_DIR

import os

from pathlib import Path


class Stages:
    STAGES = [
        {
            "name": "verify_off_card",
            "comment": "Perform an off-card verification on the fuzzed CAP files",
            "optional": False,
        },
        {
            # 'install' is one of the predefined stages
            "name": "install",
            "path": "build/{version}/fuzzed.cap",
            "optional": False,
        },
    ]


class AttackBuilder(BaseBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # fix seed for every build
        self.seed = random.randint(0, 2 ** 32)
        self.rad = pyradamsa.Radamsa()

    def _build(self):
        super()._build()
        if self.version is None:
            self.fuzz_all_versions()
        else:
            self.fuzz_version(version=self.version)

    def fuzz_all_versions(self):
        # TODO versions could be changed to self.versions
        versions = self.config.get_sdk_versions("BUILD", "versions")
        for version in versions:
            self.fuzz_version(version=version)

    def fuzz_version(self, version):
        with cd(self.workdir):
            # open the original non-malicious CAP file and fuzz it
            orig_file = Path(self.workdir / "build" / version.raw / "orig.cap")
            with open(orig_file, "rb") as f:
                fuzzed = self.rad.fuzz(f.read(), seed=self.seed)

            # save the fuzzed CAP to a new file
            fuzzed_file = Path(self.workdir / "build" / version.raw / "fuzzed.cap")
            with open(fuzzed_file, "wb") as f:
                f.write(fuzzed)


class AttackExecutor(BaseAttackExecutor):
    def _pre_custom_stage(self, *args, **kwargs):
        """
        The `_pre_<stage-name>` is the place, where you can perform some additional setup
        in case you need to do so. The difference from the other stage methods is, that in
        case it returns something it is not saved anywhere.
        """
        pass

    def _verify_off_card(self, sdk_version, *args, **kwargs):
        """
        This is the main stage method. For example for `send` stage this is the place, where
        the `payload` is sent to the JavaCard.
        """
        verifycap_file = (
            SUBMODULES_DIR
            / "oracle_javacard_sdks"
            / (sdk_version.raw + "_kit")
            / "bin"
            / "verifycap"
        )
        api_export_root = (
            SUBMODULES_DIR
            / "oracle_javacard_sdks"
            / (sdk_version.raw + "_kit")
            / "api_export_files"
        )
        # find all the *.exp files for the SDK
        exp_files = []
        for _, _, files in os.walk(api_export_root):
            exp_files.extend([f for f in files if f.endswith(".exp")])

        fuzzed_file = self.workdir / "build" / sdk_version.raw / "fuzzed.cap"

        cmd = [verifycap_file, *exp_files, fuzzed_file]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return proc_to_dict(proc=proc)

    def _assess_verify_off_card(self, result, *args, **kwargs):
        """
        This is the method, that can interpret the results of the stage. It's main goal
        is to set the `result['success']` to either `True` or `False`.
        """
        result["success"] = result["returncode"] != 0

        return result
