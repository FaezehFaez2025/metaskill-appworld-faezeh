"""The numbers the metrics depend on, in one place."""

# How many characters from the start of a bullet make up its quote.
QUOTE_LENGTH = 80

# Names shorter than this are not used to check whether a bullet was used.
MIN_NAME_LENGTH = 6

# A later instance is treated as shorter only when it saves at least this many
# generator steps. Smaller gaps are within normal variation for these tasks.
MIN_STEP_GAIN = 5
