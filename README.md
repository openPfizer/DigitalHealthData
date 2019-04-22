# Digital Health Data Kit
This python 3 code base is a collection of libraries to extract and visualize health data from digital biomarkers. Currently, analytic scripts for the Apple Watch are available. Similar libraries for other consumer devices are to be released.

## Apple Health Data
#### Note
To export Apple Health data, open Health App on iPhone, click on profile image at top right corner, then select and agree to "Export Health Data". The resulting data file will be stored as *export.xml* within a zip folder.

**read_apple_watch_data.py** parses data for the following:

- Heart Rate in beat per minute
- Resting and Walking/Running Heart Rate in beat per minute
- Heart Rate Variability (SDNN) in milliseconds
- Distance Walked/Ran in miles
- Basal Energy Burned in calories
- Stand Hour binary variable
- Step Count data

The user chooses 
- directory of xml file, otherwise will look for in current directory
- start and end dates to filter data
- save directory for plots generated, otherwise will be saved in current directory
  
**Required dependencies**: numpy, pandas, bokeh

### Running through terminal
```python
python run.py -xml_file_path export.xml -start_date 2012-12-10 23:30:00 -end_date 2012-12-20 23:30:00
```

Note: Dates must be of the following format ('%Y-%m-%d %H:%M', '%m/%d/%y %H:%M').

When providing the source name (same as apple watch name listed in Watch app on iPhone), be mindful of special, non-ascii code characters such as apostraphes. Apple Watch name can be changed from within the Watch app.

## Questions or Issues
adan.rivas@pfizer.com, or open a GitHub issue

---
Credit to @stefanluyten and his [parser script](https://github.com/stefanluyten/HealthKitExportParser)

![](img/osbypfizer.png)

