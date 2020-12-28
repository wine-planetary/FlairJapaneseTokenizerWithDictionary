import logging

from abc import ABC, abstractmethod
from typing import List, Callable, Tuple

from segtok.segmenter import split_single, split_multi
from segtok.tokenizer import split_contractions, word_tokenizer

from flair.data import Sentence, Tokenizer, Token

log = logging.getLogger("flair")

class JapaneseTokenizerWithDictionary(Tokenizer):
    """
        Tokenizer using konoha, a third party library which supports
        multiple Japanese tokenizer such as MeCab, Janome and SudachiPy.
        For further details see:
            https://github.com/himkt/konoha
    """

    def __init__(self, tokenizer: str, sudachi_mode: str="A", user_dictionary_path: str):
        super(JapaneseTokenizer, self).__init__()

        available_tokenizers = ["mecab", "janome", "sudachi"]

        if tokenizer.lower() not in available_tokenizers:
            raise NotImplementedError(
                f"Currently, {tokenizer} is only supported. Supported tokenizers: {available_tokenizers}."
            )

        try:
            import konoha
        except ModuleNotFoundError:
            log.warning("-" * 100)
            log.warning('ATTENTION! The library "konoha" is not installed!')
            log.warning(
                '- If you want to use MeCab, install mecab with "sudo apt install mecab libmecab-dev mecab-ipadic".'
            )
            log.warning('- Install konoha with "pip install konoha[{tokenizer_name}]"')
            log.warning('  - You can choose tokenizer from ["mecab", "janome", "sudachi"].')
            log.warning("-" * 100)
            exit()

        self.tokenizer = tokenizer
        self.sentence_tokenizer = konoha.SentenceTokenizer()
        self.word_tokenizer = konoha.WordTokenizer(tokenizer, mode=sudachi_mode, user_dictionary_path=user_dictionary_path)

    def tokenize(self, text: str) -> List[Token]:
        tokens: List[Token] = []
        words: List[str] = []

        sentences = self.sentence_tokenizer.tokenize(text)
        for sentence in sentences:
            konoha_tokens = self.word_tokenizer.tokenize(sentence)
            words.extend(list(map(str, konoha_tokens)))

        # determine offsets for whitespace_after field
        index = text.index
        current_offset = 0
        previous_word_offset = -1
        previous_token = None
        for word in words:
            try:
                word_offset = index(word, current_offset)
                start_position = word_offset
            except:
                word_offset = previous_word_offset + 1
                start_position = (
                    current_offset + 1 if current_offset > 0 else current_offset
                )

            token = Token(
                text=word, start_position=start_position, whitespace_after=True
            )
            tokens.append(token)

            if (previous_token is not None) and word_offset - 1 == previous_word_offset:
                previous_token.whitespace_after = False

            current_offset = word_offset + len(word)
            previous_word_offset = current_offset - 1
            previous_token = token

        return tokens

    @property
    def name(self) -> str:
        return (
            self.__class__.__name__
            + "_"
            + self.tokenizer
        )
