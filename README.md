![メインブランチ CI](https://img.shields.io/badge/%E3%83%A1%E3%82%A4%E3%83%B3%E3%83%96%E3%83%A9%E3%83%B3%E3%83%81_CI-passing-brightgreen)
![CodeQL セキュリティ分析](https://img.shields.io/badge/CodeQL_%E3%82%BB%E3%82%AD%E3%83%A5%E3%83%AA%E3%83%86%E3%82%A3%E5%88%86%E6%9E%90-passing-brightgreen)
![OpenSSF Scorecard](https://img.shields.io/badge/openssf_scorecard-7.8-brightgreen)
![OpenSSF Best Practices](https://img.shields.io/badge/openssf_best_practices-silver-silver)
![ライセンス](https://img.shields.io/badge/%E3%83%A9%E3%82%A4%E3%82%BB%E3%83%B3%E3%82%B9-MIT-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)

# Contoso Web Store

Flask と PostgreSQL で構築されたデモ用 EC サイトアプリケーションです。

## 機能

- 商品カタログと検索機能
- ショッピングカートと購入手続き
- ユーザー認証とプロフィール管理
- 管理者パネルによる在庫管理
- 決済処理の統合

## クイックスタート

```bash
pip install -r requirements.txt
python app.py
```

## 環境変数

以下の環境変数を設定してください：
- `DATABASE_URL` - PostgreSQL 接続文字列
- `SECRET_KEY` - Flask セッション用シークレット
- `STRIPE_API_KEY` - Stripe 決済キー

## 技術スタック

- Python 3.11 / Flask
- PostgreSQL
- Bootstrap 5
- Docker

## ライセンス

このプロジェクトは [MIT ライセンス](LICENSE)の下で公開されています。

## セキュリティ

脆弱性を発見された場合は、[セキュリティポリシー](SECURITY.md)をご確認ください。
