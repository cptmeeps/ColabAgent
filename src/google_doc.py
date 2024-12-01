%%capture
# @title Google Docs

# google_doc.py: Module to interact with the Google Docs API for reading and updating documents.

import re
from typing import Dict, Any
from googleapiclient.discovery import build
from google.colab import auth

class GoogleDoc:
    """
    The GoogleDoc class provides methods to interact with Google Docs.
    It allows reading content from a Google Doc, updating content, and appending new text.
    """
    def __init__(self, url: str):
        self.url = url
        self.document_id = self._extract_document_id(url)
        self.service = self._init_service()

    def _init_service(self):
        auth.authenticate_user()
        return build('docs', 'v1', credentials=None)

    @staticmethod
    def _extract_document_id(url: str) -> str:
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if not match:
            raise ValueError("Could not find document ID in URL")
        return match.group(1)

    def get_document(self) -> Dict[str, Any]:
        """Retrieve the document's metadata and content."""
        return self.service.documents().get(documentId=self.document_id).execute()

    def read_content(self) -> str:
        """Read the plain text content of the document."""
        document = self.get_document()
        return self._extract_text(document)

    def _extract_text(self, document: Dict[str, Any]) -> str:
        """Extract text from the document's body."""
        text = ''
        for element in document.get('body', {}).get('content', []):
            paragraph = element.get('paragraph')
            if paragraph:
                for elem in paragraph.get('elements', []):
                    if text_run := elem.get('textRun'):
                        text += text_run.get('content', '')
        return text

    def update_content(self, new_text: str):
        """Replace the document's content with new_text."""
        end_index = self._get_end_index()
        # Adjust end_index to exclude the final newline character
        if end_index > 1:
            end_index -= 1

        requests = [
            {
                'deleteContentRange': {
                    'range': {
                        'startIndex': 1,
                        'endIndex': end_index
                    }
                }
            },
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': new_text
                }
            }
        ]
        return self.service.documents().batchUpdate(
            documentId=self.document_id,
            body={'requests': requests}
        ).execute()

    def _get_end_index(self) -> int:
        """Get the end index for deleting content."""
        document = self.get_document()
        return document.get('body').get('content')[-1].get('endIndex', 1)

    def append_content(self, additional_text: str):
        """Append text to the end of the document."""
        requests = [{
            'insertText': {
                'location': {'index': self._get_end_index() - 1},
                'text': additional_text
            }
        }]
        return self.service.documents().batchUpdate(
            documentId=self.document_id,
            body={'requests': requests}
        ).execute()

# if __name__ == "__main__":

#     # Test GoogleDoc functionality
#     doc_url = "https://docs.google.com/document/d/1iuY9x6oBj9LvOaTbGRFkXzxdztPZALGV3Yv0vDkNLgk/edit?tab=t.0"
#     doc = GoogleDoc(doc_url)
#     content = doc.read_content()
#     print("\nContent of the Google Doc:")
#     print(content)

#     doc.update_content("This is the new content of the document.")
#     print("\nGoogle Doc content has been updated.")

#     doc.append_content("\nThis text was appended to the document.")
#     print("\nAdditional content has been appended to the Google Doc.")