# DeltaLog
Project to automate the extraction of logs to spreadsheet. It allows to measure timings between defined traces in a JSON config file.

## How to use
### Command Line
```
deltaLogs.py [yourLogFile] [yourJsonConfigFile]
```
### JSON config file
```json
{
    "outputPath": "/path/where/to/save/file",
    "outputName": "outputFileName",
    "timestampFormat": "%H:%M:%S,%f",
    "splitCharacter": "-",
    "timeBetween": [
        [
            {
                "start trace 1"
            },
            {
                "target trace 1"
            }
        ],
        [
            {
                "start trace 2"
            },
            {
                "target trace 2"
            }
        ]
    ]
}
```
#

## TODO
- Support time delta with same trace (not possible now)
- Improve time parsing and get rid of *splitCharacter* in JSON file (for now we assume timestamp is at the beginning of the line)
- Support multiple log files and cross-measurements (time between trace in file 1 and trace in file 2)
- Provide examples
- Support CSV output
- Create package and bin release
