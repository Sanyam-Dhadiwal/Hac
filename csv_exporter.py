import os
from datetime import datetime, timezone
from typing import List
from types_def import Business
from logger import Logger

class CsvExporter:
    def __init__(self, output_dir: str = 'exports'):
        self.output_dir = output_dir

    async def export(self, businesses: List[Business]) -> str:
        # 1. Create output directory automatically if missing
        if not os.path.exists(self.output_dir):
            Logger.info(f'Creating exports output directory: "{self.output_dir}"')
            os.makedirs(self.output_dir, exist_ok=True)

        # 2. Generate UTC timestamp string (e.g., 2026-07-28_11-42-00) matching JS toISOString
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        
        base_filename = f"listings_{timestamp}.csv"
        file_path = os.path.join(self.output_dir, base_filename)

        # 3. Do not overwrite existing files: check and append sequence counter if file exists
        counter = 1
        while os.path.exists(file_path):
            base_filename = f"listings_{timestamp}_{counter}.csv"
            file_path = os.path.join(self.output_dir, base_filename)
            counter += 1

        # 4. Build CSV data rows with all parsed fields
        headers = ['Name', 'Rating', 'Address', 'Phone', 'Verified']
        rows = [','.join(headers)]

        for biz in businesses:
            line = [
                self.escape_csv_field(biz.get('name')),
                self.escape_csv_field(biz.get('rating')),
                self.escape_csv_field(biz.get('address')),
                self.escape_csv_field(biz.get('phone')),
                self.escape_csv_field('Yes' if biz.get('verified') else 'No')
            ]
            rows.append(','.join(line))

        # 5. Write the CSV content to the target file
        csv_content = '\n'.join(rows)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        Logger.success(f'Successfully exported {len(businesses)} records to: "{file_path}"')
        return file_path

    def escape_csv_field(self, value) -> str:
        if value is None:
            return ''

        escaped = str(value).strip()

        # Check if the value contains elements requiring wrapping quotes
        if '"' in escaped or ',' in escaped or '\n' in escaped or '\r' in escaped:
            # Escape double quotes by doubling them
            escaped = escaped.replace('"', '""')
            # Wrap the field in double quotes
            escaped = f'"{escaped}"'

        return escaped
