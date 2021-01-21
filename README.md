# CKAN load testing tool

## Base test

Run basic tests just for basic CKAN URLs

```
cd locust
locust --config base.conf -H http://catalog.data.gov --csv=results
```
### Sample results

```
 Name                                                          # reqs      # fails  |     Avg     Min     Max  Median  |   req/s failures/s
--------------------------------------------------------------------------------------------------------------------------------------------
 GET /                                                             41     0(0.00%)  |    3394     849   11247    2900  |    0.69    0.00
 GET /group                                                        37     3(8.11%)  |    1737     605    6094     930  |    0.62    0.05
 GET /harvest                                                      33     0(0.00%)  |    2252     662    7235    1300  |    0.55    0.00
 GET /organization                                                 36     1(2.78%)  |    2274     598    6929    1300  |    0.60    0.02
--------------------------------------------------------------------------------------------------------------------------------------------
 Aggregated                                                       147     4(2.72%)  |    2446     598   11247    1500  |    2.46    0.07

Response time percentiles (approximated)
 Type     Name                                                              50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|------------------------------------------------------------|---------|------|------|------|------|------|------|------|------|------|------|------|
 GET      /                                                                2900   3300   4100   5500   6600   6900  11000  11000  11000  11000  11000     41
 GET      /group                                                            930   1300   1900   2500   4900   5900   6100   6100   6100   6100   6100     37
 GET      /harvest                                                         1300   1500   2400   4400   5600   7100   7200   7200   7200   7200   7200     33
 GET      /organization                                                    1400   1600   3200   4000   5900   6900   6900   6900   6900   6900   6900     36
--------|------------------------------------------------------------|---------|------|------|------|------|------|------|------|------|------|------|------|
 None     Aggregated                                                       1500   2500   3300   4400   5900   6900   7100   7200  11000  11000  11000    147

Error report
 # occurrences      Error                                                                                               
--------------------------------------------------------------------------------------------------------------------------------------------
 2                  GET /group: ConnectionError(ProtocolError('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')))
 1                  GET /organization: ConnectionError(ProtocolError('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')))
 1                  GET /group: HTTPError('502 Server Error: Proxy Error for url: https://catalog.data.gov/group') 
--------------------------------------------------------------------------------------------------------------------------------------------
```

## Run test from Apache logs

First get URLs from Apache logs file

```
cd locust
python parse_apache_logs.py --apache_logs_path raw-apache.log
```

You will see the `results.txt` file with all the useful URLs to test.  
The run:  

```
locust --config from_apache.conf -H http://catalog.data.gov --csv=results
```

This will iterate over all URLs and write several CSV file with stats and failures details.  

The `parse_apache_logs` will also show you the weights of the URLs in use in this log file.

```
[{'organizations': 16}, {'datasets': 405}, {'resource': 7177}, {'api-search': 726}, {'harvests': 0}, {'api-pkg-show': 1413}, {'dataset': 43939}, {'organization-search': 6}, {'api-pkg-search': 1273}, {'groups': 3}, {'home': 177}, {'organization': 2298}, {'dataset-search': 6193}, {'harvest': 3193}, {'group-search': 2}, {'group': 1496}]
```
## Run advanced test

The advanced test uses the API call to look for real dataset, harvest sources, organization and groups before ping them.

```
locust --config advanced.conf -H http://catalog.data.gov --csv=results
```

```
 Name                                                          # reqs      # fails  |     Avg     Min     Max  Median  |   req/s failures/s
--------------------------------------------------------------------------------------------------------------------------------------------
 GET api-group-list                                                30     0(0.00%)  |    2062     570   32093     720  |    0.20    0.00
 GET api-organization-list                                         23     0(0.00%)  |     779     546    1910     640  |    0.15    0.00
 GET api-package-search                                            15     0(0.00%)  |    7103    2680   14411    6100  |    0.10    0.00
 GET api-package-search-harvest                                    29     0(0.00%)  |    2392    1086    7864    1900  |    0.19    0.00
 GET dataset                                                      442    24(5.43%)  |    2525     696   69774     950  |    2.89    0.16
 GET datasets-home                                                 22     0(0.00%)  |    3830    1987   17405    2900  |    0.14    0.00
 GET group                                                        139     0(0.00%)  |    3745    1020   66527    2200  |    0.91    0.00
 GET groups-home                                                   23     0(0.00%)  |    1673     710    8585    1200  |    0.15    0.00
 GET harvest-source                                               399     0(0.00%)  |    5371     698   73101    1400  |    2.61    0.00
 GET harvest-sources-home                                          25     0(0.00%)  |    2028     751   16267    1100  |    0.16    0.00
 GET home                                                          23     0(0.00%)  |    3816    1889   10270    3300  |    0.15    0.00
 GET organization                                                 115     0(0.00%)  |    2079     662   10627    1600  |    0.75    0.00
 GET organizations-home                                            20     0(0.00%)  |    8518     907   66581    1400  |    0.13    0.00
--------------------------------------------------------------------------------------------------------------------------------------------
 Aggregated                                                      1305    24(1.84%)  |    3606     546   73101    1300  |    8.54    0.16

Response time percentiles (approximated)
 Type     Name                                                              50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|------------------------------------------------------------|---------|------|------|------|------|------|------|------|------|------|------|------|
 GET      api-group-list                                                    760   1100   1200   1200   2600   4200  32000  32000  32000  32000  32000     30
 GET      api-organization-list                                             640    650   1000   1100   1200   1200   1900   1900   1900   1900   1900     23
 GET      api-package-search                                               6100   8300   9000  12000  12000  14000  14000  14000  14000  14000  14000     15
 GET      api-package-search-harvest                                       1900   2200   2500   2700   5400   6000   7900   7900   7900   7900   7900     29
 GET      dataset                                                           950   1100   1200   1600   3700   4900  32000  33000  70000  70000  70000    442
 GET      datasets-home                                                    2900   3000   3500   3600   7000   7800  17000  17000  17000  17000  17000     22
 GET      group                                                            2200   2500   2800   3000   5000   9700  33000  38000  67000  67000  67000    139
 GET      groups-home                                                      1200   1300   1400   1500   1800   5500   8600   8600   8600   8600   8600     23
 GET      harvest-source                                                   1400   6600   7900   8400   9400  14000  37000  39000  73000  73000  73000    399
 GET      harvest-sources-home                                             1100   1400   1400   1800   4600   4600  16000  16000  16000  16000  16000     25
 GET      home                                                             3300   3800   4200   4600   4800   8500  10000  10000  10000  10000  10000     23
 GET      organization                                                     1600   2000   2300   2800   3300   4300   9600  10000  11000  11000  11000    115
 GET      organizations-home                                               1400   1600   1900   7400  66000  67000  67000  67000  67000  67000  67000     20
--------|------------------------------------------------------------|---------|------|------|------|------|------|------|------|------|------|------|------|
 None     Aggregated                                                       1300   2000   2900   4000   8300   9900  32000  37000  70000  73000  73000   1305

Error report
 # occurrences      Error                                                                                               
--------------------------------------------------------------------------------------------------------------------------------------------
 24                 GET dataset: HTTPError('500 Server Error: Internal Server Error for url: dataset',)                 
--------------------------------------------------------------------------------------------------------------------------------------------
```