
import json
import os

class ScreenTimeAnalyzer:
    """A class to analyze screen time data from a JSON log file (times in seconds)."""

    def __init__(self, json_file_path):
        """Initialize with the path to the JSON file."""
        self.json_file_path = json_file_path
        self.data = {}
        self.load_data()

    def load_data(self):
        """Load JSON data from file."""
        try:
            with open(self.json_file_path, 'r') as file:
                self.data = json.load(file)
            print(f"Successfully loaded data from {self.json_file_path}")
            print(f"Found {len(self.data)} days of data")
        except FileNotFoundError:
            print(f"Error: File '{self.json_file_path}' not found.")
            self.data = {}
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format - {e}")
            self.data = {}
        except Exception as e:
            print(f"Error loading file: {e}")
            self.data = {}

    def get_all_unique_keys(self):
        """Get all unique application/process names across all days."""
        unique_keys = set()
        for date, apps in self.data.items():
            unique_keys.update(apps.keys())
        return sorted(unique_keys)

    def sum_key_values(self, key_name):
        """Sum up all values for a specific key across all days."""
        if not self.data:
            print("No data loaded. Please check the file.")
            return 0

        total_seconds = 0
        days_found = []

        for date, apps in self.data.items():
            if key_name in apps:
                total_seconds += apps[key_name]
                days_found.append(date)

        return total_seconds, days_found

    def search_keys(self, search_term):
        """Search for keys containing a specific term (case-insensitive)."""
        if not self.data:
            print("No data loaded. Please check the file.")
            return []

        all_keys = self.get_all_unique_keys()
        matching_keys = [key for key in all_keys 
                        if search_term.lower() in key.lower()]
        return matching_keys

    def get_top_apps_by_total_time(self, top_n=10):
        """Get top N apps by total time across all days."""
        if not self.data:
            print("No data loaded. Please check the file.")
            return []

        app_totals = {}

        # Sum up time for each app across all days
        for date, apps in self.data.items():
            for app, time_spent in apps.items():
                app_totals[app] = app_totals.get(app, 0) + time_spent

        # Sort by total time (descending)
        sorted_apps = sorted(app_totals.items(), key=lambda x: x[1], reverse=True)
        return sorted_apps[:top_n]

    def analyze_key_usage_by_date(self, key_name):
        """Analyze how a specific key's usage varies by date."""
        if not self.data:
            print("No data loaded. Please check the file.")
            return {}

        usage_by_date = {}
        for date, apps in self.data.items():
            if key_name in apps:
                usage_by_date[date] = apps[key_name]

        return dict(sorted(usage_by_date.items()))

    def convert_seconds_to_readable(self, seconds):
        """Convert seconds to a readable format (hours, minutes, seconds)."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    def convert_seconds_to_hours_minutes(self, seconds):
        """Convert seconds to hours and minutes (ignoring seconds for cleaner display)."""
        total_minutes = seconds // 60
        hours = total_minutes // 60
        minutes = total_minutes % 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def interactive_analyzer(self):
        """Run an interactive session for analyzing the data."""
        if not self.data:
            print("No data loaded. Exiting.")
            return

        print("\n" + "="*60)
        print("         SCREEN TIME ANALYZER (TIME IN SECONDS)")
        print("="*60)

        while True:
            print("\nChoose an option:")
            print("1. Sum values for a specific key")
            print("2. Search for keys containing a term")
            print("3. Show top apps by total time")
            print("4. Show all unique keys")
            print("5. Analyze key usage by date")
            print("6. Exit")

            choice = input("\nEnter your choice (1-6): ").strip()

            if choice == '1':
                self.handle_sum_key()
            elif choice == '2':
                self.handle_search_keys()
            elif choice == '3':
                self.handle_top_apps()
            elif choice == '4':
                self.handle_show_all_keys()
            elif choice == '5':
                self.handle_analyze_by_date()
            elif choice == '6':
                print("\nGoodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")

    def handle_sum_key(self):
        """Handle the sum key functionality."""
        key_name = input("\nEnter the exact key name (case-sensitive): ").strip()

        if not key_name:
            print("Key name cannot be empty.")
            return

        total_seconds, days_found = self.sum_key_values(key_name)

        if total_seconds == 0:
            print(f"\nKey '{key_name}' not found in any day.")
            # Suggest similar keys
            similar_keys = self.search_keys(key_name)
            if similar_keys:
                print("\nDid you mean one of these?")
                for i, key in enumerate(similar_keys[:5], 1):
                    print(f"  {i}. {key}")
        else:
            print(f"\n{'='*50}")
            print(f"Results for: {key_name}")
            print(f"{'='*50}")
            print(f"Total time: {total_seconds:,} seconds ({self.convert_seconds_to_readable(total_seconds)})")
            print(f"Total time (simplified): {self.convert_seconds_to_hours_minutes(total_seconds)}")
            print(f"Found on {len(days_found)} days")
            print(f"Average per day: {total_seconds/len(days_found):.0f} seconds ({self.convert_seconds_to_hours_minutes(int(total_seconds/len(days_found)))})")

            if len(days_found) <= 10:
                print(f"\nDates found: {', '.join(days_found)}")
            else:
                print(f"\nFirst 5 dates: {', '.join(days_found[:5])}")
                print(f"Last 5 dates: {', '.join(days_found[-5:])}")

    def handle_search_keys(self):
        """Handle the search keys functionality."""
        search_term = input("\nEnter search term: ").strip()

        if not search_term:
            print("Search term cannot be empty.")
            return

        matching_keys = self.search_keys(search_term)

        if matching_keys:
            print(f"\nFound {len(matching_keys)} keys containing '{search_term}':")
            for i, key in enumerate(matching_keys, 1):
                print(f"  {i:2d}. {key}")
        else:
            print(f"\nNo keys found containing '{search_term}'.")

    def handle_top_apps(self):
        """Handle the top apps functionality."""
        try:
            top_n = int(input("\nEnter number of top apps to show (default 10): ") or "10")
        except ValueError:
            top_n = 10

        top_apps = self.get_top_apps_by_total_time(top_n)

        print(f"\n{'='*70}")
        print(f"TOP {top_n} APPS BY TOTAL TIME")
        print(f"{'='*70}")
        print(f"{'Rank':<4} {'App Name':<35} {'Total Time':<20} {'Seconds':<10}")
        print("-" * 70)

        for i, (app, total_seconds) in enumerate(top_apps, 1):
            time_str = self.convert_seconds_to_hours_minutes(total_seconds)
            print(f"{i:<4} {app:<35} {time_str:<20} {total_seconds:,}")

    def handle_show_all_keys(self):
        """Handle showing all unique keys."""
        all_keys = self.get_all_unique_keys()

        print(f"\nFound {len(all_keys)} unique keys:")
        print("="*50)

        for i, key in enumerate(all_keys, 1):
            print(f"{i:3d}. {key}")

        print("\nTip: You can copy any of these key names to sum their values.")

    def handle_analyze_by_date(self):
        """Handle analyzing key usage by date."""
        key_name = input("\nEnter the exact key name to analyze by date: ").strip()

        if not key_name:
            print("Key name cannot be empty.")
            return

        usage_by_date = self.analyze_key_usage_by_date(key_name)

        if not usage_by_date:
            print(f"\nKey '{key_name}' not found in any day.")
            return

        print(f"\n{'='*80}")
        print(f"USAGE BY DATE FOR: {key_name}")
        print(f"{'='*80}")
        print(f"{'Date':<12} {'Seconds':<10} {'Time (h:m)':<15} {'Full Time':<20}")
        print("-" * 80)

        total_seconds = 0
        for date, time_spent in usage_by_date.items():
            time_str = self.convert_seconds_to_hours_minutes(time_spent)
            full_time_str = self.convert_seconds_to_readable(time_spent)
            print(f"{date:<12} {time_spent:<10,} {time_str:<15} {full_time_str:<20}")
            total_seconds += time_spent

        print("-" * 80)
        total_time_str = self.convert_seconds_to_hours_minutes(total_seconds)
        total_full_str = self.convert_seconds_to_readable(total_seconds)
        print(f"{'TOTAL':<12} {total_seconds:<10,} {total_time_str:<15} {total_full_str:<20}")
        print(f"Average per day: {total_seconds/len(usage_by_date):.0f} seconds ({self.convert_seconds_to_hours_minutes(int(total_seconds/len(usage_by_date)))})")


# Example usage functions for direct key summing
def sum_app_time(json_file_path, app_name):
    """Quick function to sum time for a specific app."""
    analyzer = ScreenTimeAnalyzer(json_file_path)
    total_seconds, days_found = analyzer.sum_key_values(app_name)

    if total_seconds > 0:
        readable_time = analyzer.convert_seconds_to_readable(total_seconds)
        simple_time = analyzer.convert_seconds_to_hours_minutes(total_seconds)
        print(f"Total time for '{app_name}': {total_seconds:,} seconds ({readable_time}) = {simple_time}")
        print(f"Found on {len(days_found)} days")
        return total_seconds
    else:
        print(f"App '{app_name}' not found.")
        return 0


# Main execution
if __name__ == "__main__":
    # You can change this to your actual file path
    json_file_path = "screen_time_log.json"

    print("Screen Time Analyzer (Times in Seconds)")
    print("=======================================")
    print("This program analyzes screen time data from a JSON log file.")
    print(f"Looking for file: {json_file_path}")
    print("Note: All times are interpreted as seconds and converted to readable format.")

    # Check if file exists
    if os.path.exists(json_file_path):
        analyzer = ScreenTimeAnalyzer(json_file_path)

        # You can uncomment and modify these lines to directly sum specific apps
        # sum_app_time(json_file_path, "brave.exe")
        # sum_app_time(json_file_path, "Code.exe")
        # sum_app_time(json_file_path, "msedge.exe")

        # Start interactive mode
        analyzer.interactive_analyzer()

    else:
        print(f"\nFile '{json_file_path}' not found in the current directory.")
        print("Please make sure the JSON file is in the same directory as this script.")
        print("\nYou can also modify the 'json_file_path' variable in the script to point to your file.")
