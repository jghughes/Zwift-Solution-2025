"""
This module defines various string utility functions.
"""

# Standard library imports
# Local application imports

class JghString:
    
   @staticmethod
   def concat(*array_of_texts: str) -> str:
        """
        Concatenates a variable length array of texts.
        Skips texts that are null or whitespace.

        Args:
            array_of_texts (str): If any element in params array is null or empty, the element is skipped.

        Returns:
            str: Concatenated strings.
        """
        return JghString.concat_with_separator("", *array_of_texts)

   @staticmethod
   def concat_with_separator(separator: str, *array_of_texts: str) -> str:
        """
        Concatenates a variable length array of texts with a separator between each piece of text.
        Skips texts that are null or whitespace.

        Args:
            separator (str): If separator is null, an empty string is used instead.
            array_of_texts (str): If any element in params array is null or empty, the element is skipped.

        Returns:
            str: Concatenated strings.
        """

        # Rinse out all the empties
        list_of_texts = [text for text in array_of_texts if text]

        if not list_of_texts:
            return ""

        result = separator.join(list_of_texts)

        return result

   @staticmethod
   def concat_as_sentences(*array_of_texts: str) -> str:
        """
        Concatenates a variable length array of texts with a space between each piece of text.
        Skips texts that are null or whitespace.

        Args:
            array_of_texts (str): If any element in params array is null or empty, the element is skipped.

        Returns:
            str: Concatenated strings.
        """
        return JghString.concat_with_separator(" ", *array_of_texts)

   @staticmethod
   def concat_as_lines(*array_of_texts: str) -> str:
        """
        Concatenates a variable length array of texts with each piece of text on a new line.
        Skips texts that are null or whitespace.

        Args:
            array_of_texts (str): If any element in params array is null or empty, the element is skipped.

        Returns:
            str: Lines of text.
        """
        result = JghString.concat_with_separator("\n", *array_of_texts)
        return result

   @staticmethod
   def concat_as_paragraphs(*array_of_texts: str) -> str:
        """
        Concatenates a variable length array of texts with a linespace between each piece of text.
        Skips texts that are null or whitespace. The first parameter in the array will be
        the top paragraph. The last parameter will be the bottom paragraph.

        Args:
            array_of_texts (str): If any element in params array is null or empty, the element is skipped.

        Returns:
            str: Paragraphs of text.
        """

        result = JghString.concat_with_separator("\n\n", *array_of_texts)
        return result

# Example usage
def main():
    concatenated = JghString.concat("first", "", "second", "third", "")
    print(f"Concatenated:\n{concatenated}")

    concatenated_with_separator = JghString.concat_with_separator(", ", "first", "", "second", "third", "")
    print(f"Concatenated with separator:\n{concatenated_with_separator}")

    concatenated_as_sentences = JghString.concat_as_sentences("first", "", "second", "third", "")
    print(f"Concatenated as sentences:\n{concatenated_as_sentences}")

    concatenated_as_lines = JghString.concat_as_lines("first", "", "second", "third", "")
    print(f"Concatenated as lines:\n{concatenated_as_lines}")

    concatenated_as_paragraphs = JghString.concat_as_paragraphs("first", "", "second", "third", "")
    print(f"Concatenated as paragraphs:\n{concatenated_as_paragraphs}")

if __name__ == "__main__":
    main()
