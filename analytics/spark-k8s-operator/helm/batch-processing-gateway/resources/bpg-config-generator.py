#!/bin/python3

import gzip, base64

bpg_config = """
defaultSparkConf:
  spark.kubernetes.submission.connectionTimeout: 30000
  spark.kubernetes.submission.requestTimeout: 30000
  spark.kubernetes.driver.connectionTimeout: 30000
  spark.kubernetes.driver.requestTimeout: 30000
  spark.sql.debug.maxToStringFields: 75

sparkClusters:
  - weight: 100
    id: cluster-id-1
    eksCluster: arn:aws:eks:us-west-2:<REDACTED>:cluster/spark-k8s-operator
    masterUrl: https://<REDACTED>.sk1.us-west-2.eks.amazonaws.com
    caCertDataSOPS: <REDACTED>kRrMU9Wb1hEVE15TVRBek1URTFORGsxT1Zvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBTEl2ClQwcjlMZjN0M0toVXU4T2V1TzYyamd6VmhDcjNhVzhNSlR1WjdWVWY4VmRlb0E5ZDVrcjZIM3NjNzV0cVlYL0sKcGd6dVhTaCtSYTdTOU9ieERsQjVuWUErNVptemxCb3ljdWlGbHJPeVl6cGVCaThXeWxZS1UxNWcrdGdQK04yNApoRkgwb1l1UVFqQmk0citkaTJZZXlwMWdqR0pHd1ZOQUtaOG1ISmxDejVTR3ZTKzdlcUlGeEZCZGY0ajJZbWtlClhJWnVYRWRQNjJWeFNmTHRhUmFQaXlDTTYrOHQ5ZGdjM2JvNGpIOElIbXNqR1FKcXQxb2EvUDBZcEVBa1FsYm4KUzZvYmNlSTFOZVlhR3ZaQmlVM1k4UU8vd2grWDJNcXhkMmZSWkNERVAwcWRqOTRZWXozMllObVpSL29JWkpaSQpPWHRCM1lDeklTRjF1ZHpMTi9FQ0F3RUFBYU5aTUZjd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi93UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZHZ2VUUW95MjlzNGJyQ1RJaGs1QW9PeEQyODdNQlVHQTFVZEVRUU8KTUF5Q0NtdDFZbVZ5Ym1WMFpYTXdEUVlKS29aSWh2Y05BUUVMQlFBRGdnRUJBQzVRVFVpZ0JaelFQT0N2ZEIxRgpacDZUcElZTTdKNnFoUE1ldzU2NWNSNUI0TUt5cUIxbVllamF4YVJBVmVYNlgwMk04VnFoMElBYmRlSm5OYktWCkhKQUFYSWR2Q0VtcWdUNkNrNE54cWhiS3BZRmY5amRqa1Fobm5vVVh2dTdjMERqS2Nzd3lZaVR1ZEJBeURMNmgKZWtZRndmWVdWMXhGTlNQZUN2aDRORGc1cVl3TmN4d0w5T0EyVllaQzNncWR6VDBoMGttZUNiZjhseGlONldtbgppWHhsaHNTYTdRdFV1cDRVZXRIUCttUzQwUzEwbTVTVXhmZjVpUlMzSlorYUFhS2xiMzluajUzU3FwR1EvM0haCnF6ZFVwSXg0anYxTm9CRDFhVll4eUh6WVZnUHE2SmxqN0VucitDN3RrbE5oZW5EZlE4SEQyM1FNM2lTVjZFb1cKblM0PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
    userTokenSOPS: <REDACTED>VzVHpnaWZRLmV5SnBjM01pT2lKcmRXSmxjbTVsZEdWekwzTmxjblpwWTJWaFkyTnZkVzUwSWl3aWEzVmlaWEp1WlhSbGN5NXBieTl6WlhKMmFXTmxZV05qYjNWdWRDOXVZVzFsYzNCaFkyVWlPaUp6Y0dGeWF5MTBaV0Z0TFdFaUxDSnJkV0psY201bGRHVnpMbWx2TDNObGNuWnBZMlZoWTJOdmRXNTBMM05sWTNKbGRDNXVZVzFsSWpvaWMzQmhjbXN0ZEdWaGJTMWhMWFJ2YTJWdUxYSnhlbU50SWl3aWEzVmlaWEp1WlhSbGN5NXBieTl6WlhKMmFXTmxZV05qYjNWdWRDOXpaWEoyYVdObExXRmpZMjkxYm5RdWJtRnRaU0k2SW5Od1lYSnJMWFJsWVcwdFlTSXNJbXQxWW1WeWJtVjBaWE11YVc4dmMyVnlkbWxqWldGalkyOTFiblF2YzJWeWRtbGpaUzFoWTJOdmRXNTBMblZwWkNJNklqSmlNbVkxT0RZMExUTmlNREV0TkRWbE9TMWlaVFV3TFRobU9EZGtZVGczTXpabU5DSXNJbk4xWWlJNkluTjVjM1JsYlRwelpYSjJhV05sWVdOamIzVnVkRHB6Y0dGeWF5MTBaV0Z0TFdFNmMzQmhjbXN0ZEdWaGJTMWhJbjAuTW1OZ2sxMjRiR2stMU9EMDFEWU1qd2pLR0VYdGJNWUxKN1dBQmlQdHM1aTBoWnZVRW9TdXlkWUc5WGo0WWNlYndYUzBjVUpFcFNuT1RJUjBrdVg3dFNjM0d5UkRKaWs4SFAyT1lOeEZyaE5IdG5BNGE0S0NoSUwwdjEwaVdSM3VScDFwbU96QW5odkNCS3VDaUdoaUE0SlNMMGR5TDlpMTdhTVFrVVZHYW1WTkdBSFYxMFJadzBKSnd5Rjh1YXpXMkMyTFlmNHZobmlyTDl4MkVsV2x0T01yRW9WUTJiM3djemx3N2xGWEFLMk5DYlJQNWxmVklfdlBOaDhTaGdVa0s3U0VzRFR0U1Y1LTBZU1FVZ3RpUzF5VlZqVi1lWjFrX2Q2Mnl6U0g2bkNzUGdSelNQakx1VHd1NEs4Ny05V1dDd3RwV0pCZW05eVcwcVROUDVCSWl3
    userName: spark-team-a
    sparkApplicationNamespace: spark-team-a
    sparkServiceAccount: spark-team-a
    sparkVersions:
      - 3.2
      - 3.1
    queues:
      - dev
      - test
      - default
      - prod
    ttlSeconds: 86400  # 1 day TTL for terminated spark application
    timeoutMillis: 180000
    sparkUIUrl: http://localhost:8080
    batchScheduler: yunikorn
    sparkConf:
      spark.kubernetes.executor.podNamePrefix: '{spark-application-resource-name}'
      spark.eventLog.enabled: "true"
      spark.kubernetes.allocation.batch.size: 2000
      spark.kubernetes.allocation.batch.delay: 1s
      spark.eventLog.dir: s3a://<ENTER_S3_BUCKET>/eventlog
      spark.history.fs.logDirectory: s3a://<ENTER_S3_BUCKET>/eventlog
      spark.hadoop.fs.s3a.impl: org.apache.hadoop.fs.s3a.S3AFileSystem
      spark.hadoop.fs.s3a.change.detection.version.required: false
      spark.hadoop.fs.s3a.change.detection.mode: none
      spark.hadoop.fs.s3a.fast.upload: true
      spark.jars.packages: org.apache.hadoop:hadoop-aws:3.2.2
      spark.hadoop.fs.s3a.aws.credentials.provider: com.amazonaws.auth.WebIdentityTokenCredentialsProvider
#      spark.hadoop.hive.metastore.uris: thrift://hms.endpoint.com:9083
      spark.sql.warehouse.dir: s3a://<ENTER_S3_BUCKET>/warehouse
      spark.sql.catalogImplementation: hive
      spark.jars.ivy: /opt/spark/work-dir/.ivy2
      spark.hadoop.fs.s3a.connection.ssl.enabled: false
    sparkUIOptions:
      ServicePort: 4040
      ingressAnnotations:
        nginx.ingress.kubernetes.io/rewrite-target: /$2
        nginx.ingress.kubernetes.io/proxy-redirect-from: http://\$host/
        nginx.ingress.kubernetes.io/proxy-redirect-to: /spark-applications/{spark-application-resource-name}/
        kubernetes.io/ingress.class: nginx
        nginx.ingress.kubernetes.io/configuration-snippet: |-
          proxy_set_header Accept-Encoding "";
          sub_filter_last_modified off;
          sub_filter '<head>' '<head> <base href="/spark-applications/{spark-application-resource-name}/">';
          sub_filter 'href="/' 'href="';
          sub_filter 'src="/' 'src="';
          sub_filter '/{{num}}/jobs/' '/jobs/';
          sub_filter "setUIRoot('')" "setUIRoot('/spark-applications/{spark-application-resource-name}/')";
          sub_filter "document.baseURI.split" "document.documentURI.split";
          sub_filter_once off;
      ingressTLS:
        - hosts:
            - localhost
          secretName: localhost-tls-secret

    driver:
      env:
        - name: STATSD_SERVER_IP
          valueFrom:
            fieldRef:
              fieldPath: status.hostIP
        - name: STATSD_SERVER_PORT
          value: "8125"
        - name: AWS_STS_REGIONAL_ENDPOINTS
          value: "regional"
    executor:
      env:
        - name: STATSD_SERVER_IP
          valueFrom:
            fieldRef:
              fieldPath: status.hostIP
        - name: STATSD_SERVER_PORT
          value: "8125"
        - name: AWS_STS_REGIONAL_ENDPOINTS
          value: "regional"

sparkImages:
  - name: apache/spark-py:v3.2.2
    types:
      - Python
    version: "3.2"
  - name: apache/spark:v3.2.2
    types:
      - Java
      - Scala
    version: "3.2"

s3Bucket: <ENTER_S3_BUCKET>
s3Folder: uploaded
sparkLogS3Bucket: <ENTER_S3_BUCKET>
sparkLogIndex: index/index.txt
batchFileLimit: 2016
sparkHistoryDns: localhost
gatewayDns: localhost
sparkHistoryUrl: http://localhost:8088
allowedUsers:
  - '*'
blockedUsers:
  - blocked_user_1
queues:
  - name: dev
    maxRunningMillis: 21600000
queueTokenSOPS: {}
dbStorageSOPS:
  connectionString: jdbc:postgresql://bpg.<REDACTED>.us-west-2.rds.amazonaws.com:5432/bpg?useUnicode=yes&characterEncoding=UTF-8&useLegacyDatetimeCode=false&connectTimeout=10000&socketTimeout=30000
  user: bpg
  password: <REDACTED>
  dbName: bpg
statusCacheExpireMillis: 9000
server:
  applicationConnectors:
    - type: http
      port: 8080
logging:
  level: INFO
  loggers:
    com.apple.spark: INFO
sops: {}
"""

print(bpg_config, "\n")
compressed_yaml: bytes = gzip.compress(bytes(bpg_config, 'utf-8'))

binary_data = base64.b64encode(compressed_yaml).decode('utf-8')
print(binary_data)
