# gsc-to-gbq
Google Search Console Data to Google Big Query

--------------
## Usage   

```console
flask job 
```

```console
Usage: flask job [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  save_gsc  Save Google Search Console data in the database
```

```console
flask job save_gsc https://www.monotalk.xyz/ \
/Users/kensakurai/Programing/Bitbucket/gsc_to_bigquery/gsc_client.json \
2020-01-01 monotalk-analytics.appspot.com 'GSC Statistics/www.monotalk.xyz/'
```
