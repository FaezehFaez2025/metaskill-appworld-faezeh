"""The numbers the metrics depend on, in one place."""

# How many characters from the start of a bullet make up its quote.
QUOTE_LENGTH = 80

# Names shorter than this are not used to check whether a bullet was used.
MIN_NAME_LENGTH = 6

# An API that at least this share of the tasks call is a setup API (such as complete_task).
# The agent calls it in almost every task anyway, so finding it, or one of its arguments, in a
# reply does not show that the agent used a bullet.
MIN_TASK_SHARE_FOR_SETUP_API = 0.5

# An argument taken by at least this many APIs is too common to show that a lesson was used.
COMMON_ARGUMENT_MIN_APIS = 10

# A later instance is treated as shorter only when it saves at least this many
# generator steps. Smaller gaps are within normal variation for these tasks.
MIN_STEP_GAIN = 5
