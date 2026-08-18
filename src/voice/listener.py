import speech_recognition as sr


class VoiceListener:

    def __init__(self):

        self.recognizer = sr.Recognizer()

        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.7
        self.recognizer.phrase_threshold = 0.3

        self.microphone = sr.Microphone()


    def listen(self) -> str:

        try:

            with self.microphone as source:

                print("\nListening...")

                audio = self.recognizer.listen(
                    source,
                    timeout=None,
                    phrase_time_limit=10
                )

            languages = [
                "en-IN",
                "bn-IN",
                "hi-IN",
                "ru-RU",
                "es-ES"
            ]

            for language in languages:

                try:

                    text = self.recognizer.recognize_google(
                        audio,
                        language=language
                    )

                    if text:

                        print(
                            f"You ({language}): {text}"
                        )

                        return text

                except sr.UnknownValueError:
                    continue

                except sr.RequestError as error:

                    print(
                        "Speech recognition error:",
                        error
                    )

                    return ""

            print(
                "I couldn't understand what you said."
            )

            return ""

        except Exception as error:

            print(
                "Microphone error:",
                error
            )

            return ""
