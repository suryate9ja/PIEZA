# Performance Optimization Report: Data Caching for Google Sheets API

## Current Situation
The `fetch_transactions` function in `utils.py` is called every time a user interacts with the Streamlit app. This function makes an expensive network call to the Google Sheets API via `worksheet.get_all_records()`.

## Identified Inefficiency
- **High Latency:** Every UI interaction triggers a full re-fetch of all transaction records from Google Sheets, adding significant delay to the user experience.
- **Redundant I/O:** The data only changes when a transaction is added or deleted, yet it is fetched on every script re-run.
- **API Rate Limits:** Frequent calls to the Google Sheets API increase the risk of hitting rate limits, which could lead to application downtime.

## Proposed Optimization
Implement `@st.cache_data` for the `fetch_transactions` function and manually invalidate the cache whenever data is modified (added or deleted).

## Expected Impact
- **Latency Reduction:** Subsequent re-runs after the first fetch will take milliseconds (reading from memory) instead of seconds (network I/O).
- **Improved Responsiveness:** The UI will feel much more "snappy" during navigation and interaction.
- **Efficiency:** Drastic reduction in the number of API calls to Google Cloud.

## Theoretical Baseline
| Metric | Without Caching | With Caching (Cache Hit) | Improvement |
|--------|-----------------|--------------------------|-------------|
| Data Retrieval Time | ~500ms - 2000ms+ (Network dependent) | < 10ms (Memory access) | ~50x - 200x faster |
| API Calls per Interaction | 1 | 0 | 100% reduction |
