"""
State Machine Module for PyLockWare
Transforms functions into state machines to obfuscate control flow
"""
from pathlib import Path
from typing import Dict, Any
from pylockware.core.module_base import ModuleBase
from pylockware.transforms.state_machine_transformer import StateMachineTransformer


class StateMachineModule(ModuleBase):
    """
    Module that transforms functions into state machines to obfuscate control flow
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name_gen_settings = self.config.get('name_gen', 'english')
        self.entry_point = self.config.get('entry_point', None)
        self.add_junk_states = self.config.get('add_junk_states', True)

    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Process the project by transforming functions into state machines

        Args:
            project_path: Path to the original project
            output_path: Path to the output directory

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            transformer = StateMachineTransformer(
                name_gen_settings=self.name_gen_settings,
                add_junk_states=self.add_junk_states
            )

            for py_file in output_path.rglob("*.py"):
                if py_file.name not in ["obfuscator.py", "state_machine_transformer.py", "antidebug_llvm.py", "antidebug_crossplatform.py"]:
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            original_code = f.read()

                        transformed_code = transformer.apply_transformation(original_code)

                        if transformed_code != original_code:
                            with open(py_file, 'w', encoding='utf-8') as f:
                                f.write(transformed_code)

                    except Exception as e:
                        pass

            return True
        except Exception as e:
            return False

    def validate_config(self) -> bool:
        """
        Validate the module's configuration

        Returns:
            True if configuration is valid, False otherwise
        """
        # State machine module doesn't have specific validation requirements
        return True