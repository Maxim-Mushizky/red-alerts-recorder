import yaml
from typing import Any, Dict, Optional, Type, TypeVar
from pathlib import Path

T = TypeVar('T')


class YamlFileReader:
    """
    A class responsible for reading and parsing a YAML file.

    This class adheres to the Single Responsibility Principle (SRP) by encapsulating
    the logic for reading from a YAML file and parsing its contents.

    Attributes:
        file_path (Path): The path to the YAML file to be read.
    """

    def __init__(self, file_path: str):
        """
        Initializes the YamlFileReader with the path to the YAML file.

        Args:
            file_path (str): The path to the YAML file to be read.
        """
        self.file_path = Path(file_path)

    def read(self) -> str:
        """
        Reads the content of the YAML file.

        This method handles only reading the file's content and returns it as a string.
        It does not perform any parsing or processing.

        Returns:
            str: The content of the YAML file as a raw string.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            IOError: If there is an error reading the file.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"File {self.file_path} not found.")

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except IOError as e:
            raise IOError(f"Error reading the file {self.file_path}: {e}")


class YamlParser:
    """
    A class responsible for parsing YAML content.

    This class adheres to the Single Responsibility Principle (SRP) by encapsulating
    the logic for parsing YAML strings into Python dictionaries.

    Attributes:
        raw_yaml (str): The raw YAML content as a string.
    """

    def __init__(self, raw_yaml: str):
        """
        Initializes the YamlParser with the raw YAML content.

        Args:
            raw_yaml (str): The raw YAML content to be parsed.
        """
        self.raw_yaml = raw_yaml

    def parse(self) -> Dict[str, Any]:
        """
        Parses the raw YAML content into a Python dictionary.

        This method uses the PyYAML library to parse the YAML string.

        Returns:
            Dict[str, Any]: The parsed YAML content as a Python dictionary.

        Raises:
            yaml.YAMLError: If there is an error while parsing the YAML content.
        """
        try:
            return yaml.safe_load(self.raw_yaml)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML content: {e}")

    def get_section(self, section: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific section of the parsed YAML content.

        Args:
            section (str): The top-level section (key) to retrieve from the YAML content.

        Returns:
            Optional[Dict[str, Any]]: The content of the specified section as a Python dictionary,
                                      or None if the section does not exist.
        """
        parsed_content = self.parse()
        return parsed_content.get(section)


class YamlFileProcessor:
    """
    A high-level class that reads and parses a YAML file.

    This class adheres to the Dependency Inversion Principle (DIP) by depending on
    abstractions (the YamlFileReader and YamlParser classes) rather than low-level
    implementations.

    Attributes:
        reader (YamlFileReader): An instance of the YamlFileReader class.
        parser (YamlParser): An instance of the YamlParser class.
    """

    def __init__(self, file_path: str):
        """
        Initializes the YamlFileProcessor with the path to the YAML file.

        Args:
            file_path (str): The path to the YAML file to be processed.
        """
        self.reader = YamlFileReader(file_path)

    def process(self, section: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes the YAML file by reading its content and parsing it.

        This method orchestrates the file reading and parsing using the YamlFileReader
        and YamlParser classes. It can either return the entire parsed content or a
        specific section of the YAML file.

        Args:
            section (Optional[str]): The top-level section of the YAML file to retrieve.
                                     If None, the entire YAML file will be returned.

        Returns:
            Dict[str, Any]: The parsed YAML content or the specified section as a dictionary.
        """
        # Read the file content
        raw_yaml = self.reader.read()

        # Parse the content
        parser = YamlParser(raw_yaml)

        if section:
            section_content = parser.get_section(section)
            if section_content is None:
                raise ValueError(f"Section '{section}' not found in the YAML file.")
            return section_content

        return parser.parse()

    def parse_to_object(self, section: str, obj_class: Type[T]) -> T:
        """
        Parses a specific YAML section into a Python object (dataclass).

        Args:
            section (str): The top-level section of the YAML file to retrieve.
            obj_class (Type[T]): The Python dataclass type to map the section data to.

        Returns:
            T: An instance of the provided dataclass type with values populated from the YAML section.

        Raises:
            ValueError: If the section does not exist or cannot be mapped to the dataclass.
        """
        # Process and get the section content
        section_data = self.process(section=section)

        # Map the dictionary data to the dataclass
        try:
            obj = obj_class(**section_data)
            return obj
        except TypeError as e:
            raise ValueError(f"Error mapping YAML section to object: {e}")
