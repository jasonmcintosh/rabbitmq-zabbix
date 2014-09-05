rabbitmq-zabbix
=======================

Zabbix 経由で RabbitMQ キューとサーバーをモニタする為のテンプレート。

## なぜこれを作ったか:
SNMP プラグインは公式にサポートされているプラグインではないので、rabbitmqctl ベースのモニタは大変遅いので。

## どんなもの:
python のスクリプト群、Zabbix テンプレート、及び自動発見の為の関連データ。

## 使い方:
1. /etc/zabbix/ フォルダにファイルをインストールし、Zabbix がアクセスできるパーミッションに変える。
2. 設定を行う（下記参照）
3. テンプレートを Zabbix サーバーにインポートする。
4. zabbix_sender がインストールされていることを確認する。
5. 注意: プロセスがタイムアウトしていないか確認する。処理に3秒以上かかるようなデータやキューが RabbitMQ 内にあるとこの現象が起きることがある。（以下、翻訳省略）
6. ローカルの zabbix agent を再起動する。

## 設定:
オプションで .rab.auth ファイルを scripts/ ディレクトリ以下に作成しても良い。このファイルでデフォルトパラメータを変更することができる。フォーマットは `変数=値` で、1行に1つ記述できる。デフォルト値は次の通り:

    USERNAME=guest
    PASSWORD=guest
    CONF=/etc/zabbix/zabbix_agent.conf

このファイルにフィルタを追加することもでき、そうするとどのキューをモニタするかを厳格化できる。このアイテムは JSONでエンコードされた文字列である。使用するのが柔軟になるようなフォーマットになっている。フィルタするために、単一のオブジェクトまたはオブジェクトのリストを設定することもできる。使用可能なキーは、status, node, name, consumers, vhost, durable,
exclusive_consumer_tag, auto_delete, memory, policy である。

例えば次のフィルタは全ての durable なキューを見つける:
`FILTER='{"durable": true}'`

指定した vhost に対する durable なキューのみに絞る場合は以下の様なフィルタになる:
`FILTER='{"durable": true, "vhost": "mine"}'`

キュー名のリストを出すには、以下のようなフィルタを設定:
`FILTER='[{"name": "mytestqueuename"}, {"name": "queue2"}]'`

将来、フィルタは正規表現や除外したキューを指定できるように改善されるかもしれない。

## 変更
* zabbix_sender を用いてデータをリクエストするように更新。（以下翻訳略）
* オブジェクト一覧を扱えるようにフィルタを更新。

## 未来のアイデア
結果をローカルにキャッシュする機能（けど RabbitMQ を殺しすぎるかも）
アイデアがアレばお気軽に mcintoshj@gmail.com までメールください。


## Definite kudos to some of the other developers around the web.  In particular,
* Python Scripts: https://github.com/kmcminn/rabbit-nagios
* Base idea for the Rabbit template:  https://github.com/alfss/zabbix-rabbitmq
* Also need to thank Lewis Franklin https://github.com/brolewis for his contributions!
