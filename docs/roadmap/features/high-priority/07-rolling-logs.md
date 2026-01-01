# Rolling Logs by Date

**Priority**: High  
**Status**: Not Started  
**Phase**: Phase 3 - Conversation Management (Q1 2026)  
**Estimated Timeline**: Q1 2026

---

## Description

Implement log rotation by date to manage log file sizes and improve log management. This feature ensures log files don't grow indefinitely and provides better organization for troubleshooting and log archival.

**Key Goals**:
- Rotate logs daily at midnight
- Keep logs for configurable retention period
- Compress old log files to save space
- Organize logs by date for easy access
- Prevent log files from growing too large

---

## Use Cases

1. **Log File Management**: Prevent log files from growing too large
2. **Troubleshooting**: Easier to find logs from specific dates
3. **Disk Space**: Compress old logs to save disk space
4. **Log Archival**: Easy to archive old logs for compliance/backup
5. **Performance**: Smaller log files improve log reading performance

---

## Implementation Details

### Log Rotation Strategy

#### Rotation Schedule

- **Rotation Time**: Daily at midnight (00:00)
- **Rotation Interval**: 1 day
- **Retention Period**: Configurable (default: 30 days)
- **File Naming**: `cv_mailer_YYYY-MM-DD.log`

#### Log File Structure

**Current Log File** (active):
- `logs/cv_mailer.log` - Current day's log file

**Rotated Log Files**:
- `logs/cv_mailer_2026-01-01.log` - Logs from January 1, 2026
- `logs/cv_mailer_2026-01-02.log` - Logs from January 2, 2026
- etc.

**Compressed Log Files** (optional):
- `logs/cv_mailer_2026-01-01.log.gz` - Compressed logs from January 1, 2026
- `logs/cv_mailer_2026-01-02.log.gz` - Compressed logs from January 2, 2026

**Archive Directory** (optional):
- `logs/archive/cv_mailer_2026-01-01.log.gz` - Archived logs

### Implementation

#### Python Logging Handler

Use Python's `logging.handlers.TimedRotatingFileHandler`:

```python
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler(
    filename='logs/cv_mailer.log',
    when='midnight',
    interval=1,
    backupCount=LOG_RETENTION_DAYS,
    encoding='utf-8',
    delay=False
)
```

**Parameters**:
- `filename`: Base log file name
- `when`: Rotation time ('midnight', 'H', 'D', etc.)
- `interval`: Rotation interval (1 = daily)
- `backupCount`: Number of backup files to keep (retention period)
- `encoding`: UTF-8 for proper character encoding
- `delay`: False to create file immediately

#### Log Compression

**Option 1: Built-in Compression**
- `TimedRotatingFileHandler` doesn't support compression natively
- Need custom handler or post-rotation compression

**Option 2: Custom Handler**
- Extend `TimedRotatingFileHandler` to add compression
- Compress log files after rotation
- Use gzip compression

**Option 3: Post-Rotation Script**
- Separate script/process to compress old log files
- Runs periodically (e.g., daily cron job)
- Compresses files older than N days

**Recommendation**: Option 2 (Custom Handler) for cleaner implementation

#### Code Changes

**Update Logging Configuration**:

File: `src/cv_mailer/utils/logging_utils.py` or logging configuration file

```python
import logging
from logging.handlers import TimedRotatingFileHandler
from cv_mailer.config import Config
import gzip
import os

class CompressedRotatingFileHandler(TimedRotatingFileHandler):
    """Custom handler that compresses rotated log files."""
    
    def rotation_filename(self, default_name):
        """Return filename for rotated file."""
        return default_name + '.gz'
    
    def rotate(self, source, dest):
        """Compress source file to destination."""
        with open(source, 'rb') as f_in:
            with gzip.open(dest, 'wb') as f_out:
                f_out.writelines(f_in)
        os.remove(source)

def setup_logging():
    """Setup logging with rotating file handler."""
    log_file = 'logs/cv_mailer.log'
    retention_days = Config.LOG_RETENTION_DAYS or 30
    compress = Config.LOG_COMPRESS if hasattr(Config, 'LOG_COMPRESS') else True
    
    if compress:
        handler = CompressedRotatingFileHandler(
            filename=log_file,
            when='midnight',
            interval=1,
            backupCount=retention_days,
            encoding='utf-8'
        )
    else:
        handler = TimedRotatingFileHandler(
            filename=log_file,
            when='midnight',
            interval=1,
            backupCount=retention_days,
            encoding='utf-8'
        )
    
    # Configure formatter, level, etc.
    # ... existing logging configuration ...
```

#### Configuration

**Environment Variables**:

Add to `.env` file and `Config` class:

- `LOG_RETENTION_DAYS` (integer, default: 30)
  - Number of days to keep log files
  - Example: `LOG_RETENTION_DAYS=90` (keep 90 days of logs)

- `LOG_COMPRESS` (boolean, default: true)
  - Whether to compress rotated log files
  - Example: `LOG_COMPRESS=true`

**Config Class Updates**:

```python
# src/cv_mailer/config/settings.py
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))
LOG_COMPRESS = os.getenv("LOG_COMPRESS", "true").lower() == "true"
```

#### Archive Directory (Optional)

**Implementation**:
- Create `logs/archive/` directory
- Move old log files (older than retention period) to archive
- Or move compressed files to archive immediately

**Benefits**:
- Keeps `logs/` directory clean
- Easy to archive/backup old logs
- Separates active logs from archived logs

**Recommendation**: Implement archive directory for better organization

### Log File Cleanup

#### Automatic Cleanup

- Old log files (older than retention period) are automatically deleted
- Handled by `backupCount` parameter in `TimedRotatingFileHandler`
- Cleanup happens during rotation

#### Manual Cleanup

- Provide CLI command to manually clean old logs
- Example: `cv-mailer clean-logs --days=30`
- Useful for one-time cleanup or different retention policies

---

## Technical Considerations

### File Naming

**Current Implementation**:
- `cv_mailer.log` - Current log file
- `cv_mailer.log.2026-01-01` - Rotated log file (default TimedRotatingFileHandler naming)

**Desired Naming**:
- `cv_mailer.log` - Current log file
- `cv_mailer_2026-01-01.log` - Rotated log file (more readable)

**Solution**: Custom `rotation_filename` method in custom handler

### Compression Format

- Use gzip compression (`.gz` extension)
- Standard format, widely supported
- Good compression ratio for text logs
- Fast compression/decompression

### Performance

- Log rotation happens at midnight (low traffic time)
- Compression may take time for large log files
- Consider async compression for large files
- Don't block logging during rotation

### Disk Space

- Calculate disk space savings from compression
- Monitor log directory size
- Set reasonable retention period based on disk space
- Alert if log directory grows too large (future enhancement)

### Error Handling

- Handle file permission errors gracefully
- Handle disk full errors
- Log rotation errors (to separate error log or console)
- Fallback to non-rotating handler if rotation fails

### Backward Compatibility

- Existing log file (`cv_mailer.log`) continues to work
- New rotation starts from implementation date
- Old log files can remain as-is (don't need to migrate)
- Optional: Migrate existing log file to new format

---

## Dependencies

- Python `logging.handlers.TimedRotatingFileHandler`
- Python `gzip` module (for compression)
- Config updates for LOG_RETENTION_DAYS and LOG_COMPRESS
- Logging utility updates

---

## Related Features

- [Monitoring & Logging (Advanced)](../technical-improvements/28-monitoring-logging-advanced.md) - Advanced log aggregation and analysis
- Basic Logging (already implemented) - This feature enhances existing logging

---

## Benefits

- ✅ Prevents log files from growing too large
- ✅ Easier log file management
- ✅ Better organization (logs by date)
- ✅ Disk space savings (compression)
- ✅ Easier troubleshooting (find logs by date)
- ✅ Easier log archival and backup
- ✅ Improved log reading performance

---

## Success Criteria

- [ ] Logs rotate daily at midnight
- [ ] Old log files are deleted after retention period
- [ ] Log files are compressed (if enabled)
- [ ] Log file naming is readable (cv_mailer_YYYY-MM-DD.log)
- [ ] Configuration works (LOG_RETENTION_DAYS, LOG_COMPRESS)
- [ ] No logging interruption during rotation
- [ ] Disk space is managed efficiently
- [ ] Error handling works correctly
- [ ] Backward compatible with existing logs

---

## Configuration Examples

**Keep 30 days of logs, compress enabled** (default):
```env
LOG_RETENTION_DAYS=30
LOG_COMPRESS=true
```

**Keep 90 days of logs, no compression**:
```env
LOG_RETENTION_DAYS=90
LOG_COMPRESS=false
```

**Keep 7 days of logs, compress enabled**:
```env
LOG_RETENTION_DAYS=7
LOG_COMPRESS=true
```

---

**Last Updated**: January 2026

