import json
import unittest
from pydantic import ValidationError
from app_settings_dto import AppSettingsDataTransferObject
from jgh_serialization import JghSerialization

class TestAppSettingsDataTransferObject(unittest.TestCase):
    def setUp(self):
        self.json_data = '''
{
    "environment": {
        "name": "development"
    },
    "logging": {
        "console": {
            "loglevel": "debug",
            "messageformat": "normal"
        },
        "file": {
            "loglevel": "info",
            "messageformat": "verbose"
        }
    },
    "storage": {
        "local": {
            "relativedirpath": "logs"
        },
        "azure": {
            "connectionstring": "your-azure-connection-string",
            "container": "your-container-name",
            "blobname": "your-blob-name"
        },
        "aws": {
            "accesskey": "your-aws-access-key",
            "secretkey": "your-aws-secret-key",
            "bucket": "your-bucket-name",
            "objectname": "your-object-name"
        },
        "oracle": {
            "username": "your-oracle-username",
            "password": "your-oracle-password",
            "bucket": "your-bucket-name",
            "objectname": "your-object-name"
        }
    },
    "databases": {
        "primary": {
            "provider": "SQLServer",
            "connectionstring": "Server=myServerAddress;Database=myDataBase;User Id=myUsername;Password=myPassword;",
            "timeout": 30,
            "pooling": true,
            "maxpoolsize": 100,
            "minpoolsize": 10,
            "retrypolicy": {
                "maxretries": 3,
                "delay": 2000
            }
        },
        "secondary": {
            "provider": "SQLServer",
            "connectionstring": "Server=thirdPartyServerAddress;Database=thirdPartyDataBase;User Id=thirdPartyUsername;Password=thirdPartyPassword;",
            "timeout": 30,
            "pooling": true,
            "maxpoolsize": 100,
            "minpoolsize": 10,
            "retrypolicy": {
                "maxretries": 3,
                "delay": 2000
            }
        }
    },
    "apis": {
        "primary": {
            "baseurl": "https://api.example.com",
            "apikey": "your-api-key-here",
            "version": "v1",
            "timeout": 30,
            "retrypolicy": {
                "maxretries": 3,
                "delay": 2000
            },
            "headers": {
                "Content_Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer your-token-here",
                "User_Agent": "YourAppName/1.0",
                "Cache_Control": "no-cache",
                "Custom_Header": "custom-value",
                "Accept_Encoding": "gzip, deflate"
            },
            "endpoints": {
                "get": "/users/{id}",
                "create": "/users",
                "update": "/users/{id}",
                "delete": "/users/{id}",
                "getByFilter": "/users?filter={filter}"
            }
        },
        "secondary": {
            "baseurl": "https://secondaryapi.example.com",
            "apikey": "another-api-key-here",
            "version": "v2",
            "timeout": 30,
            "retrypolicy": {
                "maxretries": 3,
                "delay": 2000
            },
            "headers": {
                "Content_Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer another-token-here",
                "User_Agent": "YourAppName/1.0",
                "Cache_Control": "no-cache",
                "Custom_Header": "another-custom-value",
                "Accept_Encoding": "gzip, deflate"
            },
            "endpoints": {
                "get": "/products?id={id}",
                "create": "/products",
                "update": "/products?id={id}",
                "delete": "/products?id={id}",
                "getByFilter": "/products?filter={filter}"
            }
        }
    }
}
'''
    def test_app_settings_dto_with_json_loads(self):
        """
        Test that AppSettingsDataTransferObject successfully validates JSON data
        using json.loads. This test ensures that the JSON data can be parsed
        and validated against the AppSettingsDataTransferObject schema.
        """
        data = json.loads(self.json_data)
        app_settings = AppSettingsDataTransferObject(**data)
        self.assertIsInstance(app_settings, AppSettingsDataTransferObject)
        
        # Additional assertions
        self.assertEqual(app_settings.logging.console.loglevel, "debug")
        self.assertEqual(app_settings.logging.console.messageformat, "normal")
        self.assertEqual(app_settings.logging.file.loglevel, "info")
        self.assertEqual(app_settings.logging.file.messageformat, "verbose")

    def test_app_settings_dto_with_pydantic_validate(self):
        """
        Test that AppSettingsDataTransferObject successfully validates JSON data
        using Pydantic's model_validate_json method. This test ensures that the
        JSON data can be directly validated by Pydantic against the
        AppSettingsDataTransferObject schema.
        """
        try:
            app_settings = AppSettingsDataTransferObject.model_validate_json(self.json_data)
            self.assertIsInstance(app_settings, AppSettingsDataTransferObject)
            
            # Additional assertions
            self.assertEqual(app_settings.logging.console.loglevel, "debug")
            self.assertEqual(app_settings.logging.console.messageformat, "normal")
            self.assertEqual(app_settings.logging.file.loglevel, "info")
            self.assertEqual(app_settings.logging.file.messageformat, "verbose")
        except ValidationError as e:
            self.fail(f"Validation failed: {e}")

    def test_app_settings_dto_with_jgh_serialization_validate(self):
        """
        Test that AppSettingsDataTransferObject successfully validates JSON data
        using JghSerialization.validate method. This test ensures that the
        JSON data can be directly validated by JghSerialization against the
        AppSettingsDataTransferObject schema.
        """
        try:
            app_settings = JghSerialization.validate(self.json_data, AppSettingsDataTransferObject)
            self.assertIsInstance(app_settings, AppSettingsDataTransferObject)
            
            # Additional assertions
            self.assertEqual(app_settings.logging.console.loglevel, "debug")
            self.assertEqual(app_settings.logging.console.messageformat, "normal")
            self.assertEqual(app_settings.logging.file.loglevel, "info")
            self.assertEqual(app_settings.logging.file.messageformat, "verbose")
        except ValidationError as e:
            self.fail(f"Validation failed: {e}")

if __name__ == '__main__':
    unittest.main(verbosity=2)