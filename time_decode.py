import datetime

# Hexadecimal value provided by the SBD modem
hex_value = "ee938899"  # Replace with your hexadecimal value from AT-MSSTM

# ERA2 epoch for Iridium system time
era2_epoch = datetime.datetime(2014, 5, 11, 14, 23, 55)

# Convert the hexadecimal string to a decimal number representing the count of 90 ms intervals
interval_count = int(hex_value, 16)

# Calculate the total milliseconds since the epoch
total_milliseconds = interval_count * 90

# Create a timedelta with the total milliseconds
time_delta = datetime.timedelta(milliseconds=total_milliseconds)

# Calculate the exact datetime by adding the timedelta to the epoch
decoded_time = era2_epoch + time_delta

# Output the decoded time
print(f"Decoded Iridium Time: {decoded_time}")
