import unittest
from unittest.mock import patch, MagicMock
import sys
import json
import app # Import the app module itself for app.main()

# Assuming app.py is in the same directory or accessible via PYTHONPATH
from app import grab_source, parse_html
import requests # For requests.exceptions.HTTPError

class TestGrabSource(unittest.TestCase):

    @patch('app.requests.get')
    def test_grab_source_success(self, mock_get):
        # Configure the mock response for a successful request
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Success</body></html>"
        mock_response.raise_for_status = MagicMock() # Mock this method
        mock_get.return_value = mock_response

        source = grab_source("testuser")
        self.assertEqual(source, "<html><body>Success</body></html>")
        mock_get.assert_called_once_with("https://linktr.ee/testuser") # headers=None is not passed if headers is None
        mock_response.raise_for_status.assert_called_once()

    @patch('app.requests.get')
    @patch('app.sys.exit')
    def test_grab_source_http_error_404(self, mock_app_sys_exit, mock_requests_get): # Order matches decorators
        # Configure the mock response for a 404 error
        mock_response = MagicMock()
        mock_response.status_code = 404
        http_error = requests.exceptions.HTTPError("404 Client Error: Not Found for url")
        mock_response.raise_for_status = MagicMock(side_effect=http_error)
        mock_requests_get.return_value = mock_response

        mock_app_sys_exit.side_effect = SystemExit(1) # Ensure exit code is 1

        with self.assertRaises(SystemExit) as cm:
            grab_source("nonexistentuser")

        self.assertEqual(cm.exception.code, 1) # Check exit code
        mock_requests_get.assert_called_once_with("https://linktr.ee/nonexistentuser")
        mock_response.raise_for_status.assert_called_once()
        mock_app_sys_exit.assert_called_once_with(1)

    @patch('app.requests.get')
    @patch('app.sys.exit')
    def test_grab_source_other_request_exception(self, mock_app_sys_exit, mock_requests_get): # Order matches
        request_exception = requests.exceptions.RequestException("Some other network error")
        mock_requests_get.side_effect = request_exception

        mock_app_sys_exit.side_effect = SystemExit(1) # Ensure exit code is 1

        with self.assertRaises(SystemExit) as cm:
            grab_source("anyuser")

        self.assertEqual(cm.exception.code, 1)
        mock_requests_get.assert_called_once_with("https://linktr.ee/anyuser")
        mock_app_sys_exit.assert_called_once_with(1)


class TestParseHtml(unittest.TestCase):

    def _create_html_with_next_data(self, next_data_content):
        if isinstance(next_data_content, dict):
            next_data_str = json.dumps(next_data_content)
        else:
            next_data_str = next_data_content
        return f"""
        <html>
            <body>
                <script id="__NEXT_DATA__" crossorigin="anonymous" type="application/json">
                {next_data_str}
                </script>
            </body>
        </html>
        """

    def test_parse_html_success(self):
        mock_account_data = {
            "username": "testuser",
            "description": "Test description",
            "profilePictureUrl": "http://example.com/pic.jpg",
            "links": [
                {"title": "Link1", "url": "http://example.com/link1"},
                {"title": "Link2", "url": "http://example.com/link2"}
            ]
        }
        next_data = {
            "props": {
                "pageProps": {
                    "account": mock_account_data
                }
            }
        }
        html_source = self._create_html_with_next_data(next_data)

        expected_info = {
            "username": "testuser",
            "description": "Test description",
            "profilePictureUrl": "http://example.com/pic.jpg",
            "links": [
                {"Link1": "http://example.com/link1"},
                {"Link2": "http://example.com/link2"}
            ]
        }

        parsed_info = parse_html(html_source)
        self.assertEqual(parsed_info, expected_info)

    @patch('app.sys.exit')
    def test_parse_html_no_next_data_script(self, mock_app_sys_exit):
        html_source = "<html><body><p>No script tag</p></body></html>"
        mock_app_sys_exit.side_effect = SystemExit(1)
        with self.assertRaises(SystemExit) as cm:
            parse_html(html_source)
        self.assertEqual(cm.exception.code, 1)
        mock_app_sys_exit.assert_called_once_with(1)

    @patch('app.sys.exit')
    def test_parse_html_json_decode_error(self, mock_app_sys_exit):
        html_source = self._create_html_with_next_data("This is not valid JSON")
        mock_app_sys_exit.side_effect = SystemExit(1)
        with self.assertRaises(SystemExit) as cm:
            parse_html(html_source)
        self.assertEqual(cm.exception.code, 1)
        mock_app_sys_exit.assert_called_once_with(1)

    @patch('app.sys.exit')
    def test_parse_html_key_error_props(self, mock_app_sys_exit):
        next_data = {"wrong_props_key": {}}
        html_source = self._create_html_with_next_data(next_data)
        mock_app_sys_exit.side_effect = SystemExit(1)
        with self.assertRaises(SystemExit) as cm:
            parse_html(html_source)
        self.assertEqual(cm.exception.code, 1)
        mock_app_sys_exit.assert_called_once_with(1)

    @patch('app.sys.exit')
    def test_parse_html_key_error_page_props(self, mock_app_sys_exit):
        next_data = {"props": {"wrong_page_props_key": {}}}
        html_source = self._create_html_with_next_data(next_data)
        mock_app_sys_exit.side_effect = SystemExit(1)
        with self.assertRaises(SystemExit) as cm:
            parse_html(html_source)
        self.assertEqual(cm.exception.code, 1)
        mock_app_sys_exit.assert_called_once_with(1)

    @patch('app.sys.exit')
    def test_parse_html_key_error_account(self, mock_app_sys_exit):
        next_data = {"props": {"pageProps": {"wrong_account_key": {}}}}
        html_source = self._create_html_with_next_data(next_data)
        mock_app_sys_exit.side_effect = SystemExit(1)
        with self.assertRaises(SystemExit) as cm:
            parse_html(html_source)
        self.assertEqual(cm.exception.code, 1)
        mock_app_sys_exit.assert_called_once_with(1)

    @patch('app.sys.stderr', new_callable=MagicMock) # To check warnings
    def test_parse_html_malformed_links(self, mock_stderr):
        mock_account_data = {
            "username": "testuser",
            "description": "Test description",
            "profilePictureUrl": "http://example.com/pic.jpg",
            "links": [
                {"title": "Good Link", "url": "http://good.com"},
                "not a dict", # Malformed link
                {"title": "Missing URL"}, # Malformed link
                {"url": "http://missingtitle.com"} # Malformed link
            ]
        }
        next_data = {
            "props": {
                "pageProps": {
                    "account": mock_account_data
                }
            }
        }
        html_source = self._create_html_with_next_data(next_data)

        expected_info = {
            "username": "testuser",
            "description": "Test description",
            "profilePictureUrl": "http://example.com/pic.jpg",
            "links": [
                {"Good Link": "http://good.com"} # Capitalized "L"
            ]
        }

        parsed_info = parse_html(html_source)
        # Ensure the capitalization from app.py (x.get("title").capitalize()) is matched
        expected_info_corrected = {
            "username": "testuser",
            "description": "Test description",
            "profilePictureUrl": "http://example.com/pic.jpg",
            "links": [
                {"Good link": "http://good.com"} # capitalize() makes "Good Link" -> "Good link"
            ]
        }
        self.assertEqual(parsed_info, expected_info_corrected)
        # Check that warnings were printed to stderr for each malformed link
        self.assertGreaterEqual(mock_stderr.write.call_count, 3)


# It's generally complex to thoroughly test the __main__ block's argument parsing
# and file I/O directly with unittest.mock alone, especially with argparse.FileType.
# A common approach is to refactor the core logic of __main__ into a separate function
# that can be called with arguments, making it easier to test.
# However, for this exercise, I will add a few illustrative tests for __main__
# focusing on how it calls other functions based on arguments.
# No longer need to mock ArgumentParser as we call app.main directly with argv list.

# Patches are applied in reverse order of arguments
@patch('app.sys.exit')
@patch('builtins.print')
@patch('app.json.dump')
@patch('app.json.load') # For header file loading
@patch('app.parse_html')
@patch('app.grab_source')
class TestMainExecution(unittest.TestCase):

    # Order of mock arguments matches the actual decorator order (bottom-up from @patch)
    # @patch('app.grab_source') -> mock_grab_source (first arg after self)
    # @patch('app.parse_html') -> mock_parse_html
    # ...
    # @patch('app.sys.exit') -> mock_sys_exit (last mock arg)
    def test_main_no_username(self, mock_grab_source, mock_parse_html, mock_json_load,
                              mock_json_dump, mock_print, mock_sys_exit):

        mock_sys_exit.side_effect = SystemExit(1) # Make mock sys.exit raise SystemExit with code 1

        with self.assertRaises(SystemExit) as cm:
            app.main([]) # No arguments, so username will be None

        self.assertEqual(cm.exception.code, 1) # Check exit code
        mock_sys_exit.assert_called_once_with(1)

    def test_main_with_username_stdout(self, mock_grab_source, mock_parse_html, mock_json_load,
                                       mock_json_dump, mock_print, mock_sys_exit):

        mock_grab_source.return_value = "dummy_html_source"
        mock_parse_html.return_value = {"user": "testuser", "data": "somedata"}

        app.main(['--username', 'testuser'])

        mock_grab_source.assert_called_once_with("testuser", headers=None)
        mock_parse_html.assert_called_once_with("dummy_html_source")
        mock_print.assert_called_once_with(json.dumps({"user": "testuser", "data": "somedata"}))
        mock_json_dump.assert_not_called()
        mock_sys_exit.assert_not_called()

    # For this test, the method-specific @patch('builtins.open') is the first mock argument (mock_dev_open),
    # followed by the class-level mocks in their defined order.
    @patch('builtins.open', new_callable=MagicMock)
    def test_main_with_username_headers_outfile(self, mock_dev_open, # From this method's decorator
                                                mock_grab_source, mock_parse_html, mock_json_load,
                                                mock_json_dump, mock_print, mock_sys_exit): # From class decorators

        # This test uses a local patch for argparse.ArgumentParser to simulate file objects
        # The builtins.open mock (mock_dev_open) is not directly used here due to argparse.FileType handling.
        # However, if app.main itself called open(), mock_dev_open would be the one.

        mock_json_load.return_value = {"X-Test-Header": "true"}
        mock_grab_source.return_value = "dummy_html_source_with_headers"
        mock_parse_html.return_value = {"user": "testuser", "data": "with_headers"}

        # Patch ArgumentParser locally for this test to inject mock file objects
        with patch('argparse.ArgumentParser') as mock_ArgumentParser_local:
            # Configure the mock ArgumentParser instance
            mock_parser_instance = mock_ArgumentParser_local.return_value

            # Simulate the args object that parse_args() would return
            mock_simulated_args = MagicMock()
            mock_simulated_args.username = "testuser"

            # Create MagicMock instances for file objects
            mock_headers_file = MagicMock() # Using simple MagicMock
            mock_headers_file.name = "headers.json"
            mock_headers_file.close = MagicMock() # Add close method
            mock_simulated_args.headersFile = mock_headers_file

            mock_outfile = MagicMock() # Using simple MagicMock
            mock_outfile.name = "out.json"
            mock_outfile.close = MagicMock() # Add close method
            mock_simulated_args.outfile = mock_outfile

            mock_parser_instance.parse_args.return_value = mock_simulated_args

            # Call app.main with arguments that would trigger file processing
            app.main(['--username', 'testuser', '--headersFile', 'headers.json', '--outfile', 'out.json'])

            # Assertions
            mock_json_load.assert_called_once_with(mock_headers_file)
            mock_headers_file.close.assert_called_once()

            mock_grab_source.assert_called_once_with("testuser", headers={"X-Test-Header": "true"})
            mock_parse_html.assert_called_once_with("dummy_html_source_with_headers")

            mock_json_dump.assert_called_once_with({"user": "testuser", "data": "with_headers"}, mock_outfile)
            mock_outfile.close.assert_called_once()

            mock_print.assert_not_called()
            mock_sys_exit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
