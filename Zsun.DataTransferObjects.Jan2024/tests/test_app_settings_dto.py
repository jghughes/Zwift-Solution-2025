
import json
import unittest
from pydantic import ValidationError
from app_settings_dto import AppSettingsDataTransferObject

class TestAppSettingsDataTransferObject(unittest.TestCase):
    def setUp(self):
        self.json_data = '''
        {
          "logging": {
            "console": {
              "loglevel": "information",
              "format": "simple",
              "simpleformat": "{timestamp} [{level}] {message}",
              "verboseformat": "{timestamp} [{level}] {message} {exception}",
              "jsonformat": "{ \\"timestamp\\": \\"{timestamp}\\", \\"level\\": \\"{level}\\", \\"message\\": \\"{message}\\", \\"exception\\": \\"{exception}\\" }"
            },
            "file": {
              "loglevel": "information",
              "format": "json",
              "simpleformat": "{timestamp} [{level}] {message}",
              "verboseformat": "{timestamp} [{level}] {message} {exception}",
              "jsonformat": "{ \\"timestamp\\": \\"{timestamp}\\", \\"level\\": \\"{level}\\", \\"message\\": \\"{message}\\", \\"exception\\": \\"{exception}\\" }",
              "maxfilesize": 10485760,
              "rotation": {
                "when": "midnight",
                "interval": 1,
                "backupcount": 7
              },
              "storage": {
                "type": "local",
                "local": {
                  "path": "logs/app.log"
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
              }
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
            "external": {
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
            "exampleapi": {
              "baseurl": "https://api.example.com",
              "apikey": "your-api-key-here",
              "version": "v1",
              "timeout": 30,
              "retrypolicy": {
                "maxretries": 3,
                "delay": 2000
              },
              "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer your-token-here",
                "User-Agent": "YourAppName/1.0",
                "Cache-Control": "no-cache",
                "Custom-Header": "custom-value",
                "Accept-Encoding": "gzip, deflate"
              },
              "endpoints": {
                "get": "/users/{id}",
                "create": "/users",
                "update": "/users/{id}",
                "delete": "/users/{id}",
                "getByFilter": "/users?filter={filter}"
              }
            },
            "anotherapi": {
              "baseurl": "https://anotherapi.example.com",
              "apikey": "another-api-key-here",
              "version": "v2",
              "timeout": 30,
              "retrypolicy": {
                "maxretries": 3,
                "delay": 2000
              },
              "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer another-token-here",
                "User-Agent": "YourAppName/1.0",
                "Cache-Control": "no-cache",
                "Custom-Header": "another-custom-value",
                "Accept-Encoding": "gzip, deflate"
              },
              "endpoints": {
                "get": "/products/{id}",
                "create": "/products",
                "update": "/products/{id}",
                "delete": "/products/{id}",
                "getByFilter": "/products?filter={filter}"
              }
            }
          },
          "environment": {
            "name": "development"
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
        self.assertEqual(app_settings.logging.console.loglevel, "information")
        self.assertEqual(app_settings.logging.console.format, "simple")
        self.assertEqual(app_settings.logging.file.maxfilesize, 10485760)
        self.assertEqual(app_settings.logging.file.rotation.when, "midnight")
        self.assertEqual(app_settings.logging.file.storage.type, "local")


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
            self.assertEqual(app_settings.logging.console.loglevel, "information")
            self.assertEqual(app_settings.logging.console.format, "simple")
            self.assertEqual(app_settings.logging.file.maxfilesize, 10485760)
            self.assertEqual(app_settings.logging.file.rotation.when, "midnight")
            self.assertEqual(app_settings.logging.file.storage.type, "local")

        except ValidationError as e:
            self.fail(f"Validation failed: {e}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
