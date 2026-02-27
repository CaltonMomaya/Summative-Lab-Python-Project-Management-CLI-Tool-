import json
import os
from typing import List, Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileHandler:
    """
    Utility class for handling file operations.
    Manages reading from and writing to JSON files in the data directory.
    """
    
    DATA_DIR = 'data'
    
    @classmethod
    def ensure_data_dir(cls) -> None:
        """
        Ensure the data directory exists.
        Creates it if it doesn't exist.
        """
        if not os.path.exists(cls.DATA_DIR):
            os.makedirs(cls.DATA_DIR)
            logging.info(f"Created data directory: {cls.DATA_DIR}")
    
    @classmethod
    def get_file_path(cls, filename: str) -> str:
        """
        Get the full path for a data file.
        
        Args:
            filename: Name of the file
            
        Returns:
            str: Full path to the file
        """
        cls.ensure_data_dir()
        return os.path.join(cls.DATA_DIR, filename)
    
    @classmethod
    def load_data(cls, filename: str) -> List[Dict[str, Any]]:
        """
        Load data from a JSON file.
        
        Args:
            filename: Name of the file to load
            
        Returns:
            List[Dict]: Loaded data or empty list if file doesn't exist
        """
        file_path = cls.get_file_path(filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logging.info(f"Loaded data from {filename}")
                    return data
            else:
                logging.info(f"File {filename} does not exist, returning empty list")
                return []
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from {filename}: {e}")
            return []
        except Exception as e:
            logging.error(f"Error loading data from {filename}: {e}")
            return []
    
    @classmethod
    def save_data(cls, filename: str, data: List[Dict[str, Any]]) -> bool:
        """
        Save data to a JSON file.
        
        Args:
            filename: Name of the file to save to
            data: Data to save
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        file_path = cls.get_file_path(filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logging.info(f"Saved data to {filename}")
            return True
        except Exception as e:
            logging.error(f"Error saving data to {filename}: {e}")
            return False
    
    @classmethod
    def backup_data(cls, filename: str) -> Optional[str]:
        """
        Create a backup of a data file.
        
        Args:
            filename: Name of the file to backup
            
        Returns:
            Optional[str]: Backup filename if successful, None otherwise
        """
        file_path = cls.get_file_path(filename)
        
        if not os.path.exists(file_path):
            logging.warning(f"Cannot backup {filename}: File does not exist")
            return None
        
        backup_filename = f"{filename}.backup"
        backup_path = cls.get_file_path(backup_filename)
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            logging.info(f"Created backup: {backup_filename}")
            return backup_filename
        except Exception as e:
            logging.error(f"Error creating backup: {e}")
            return None