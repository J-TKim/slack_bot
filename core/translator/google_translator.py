import googletrans

translator = googletrans.Translator()


def translate_text(text, target_language):
    result = translator.translate(text, dest=target_language)
    return result.text


if __name__ == "__main__":
    text = "Hello World"
    target_language = "ko"
    print(translate_text(text, target_language))
