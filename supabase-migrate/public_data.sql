--
-- PostgreSQL database dump
--

\restrict lcmtBTNDf31Pj2fJVt5h55Nv0TCFmzam6uvQt7otGQV5CcsaxJAU3jVaD61QnnS

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.6 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: approach_methods; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.approach_methods (method_id, method_name, description, created_at) FROM stdin;
1	メール	電子メールでのアプローチ	2025-07-20 03:10:24.167827+00
2	電話	電話でのアプローチ	2025-07-20 03:10:24.167827+00
3	LinkedIn	LinkedInでのアプローチ	2025-07-20 03:10:24.167827+00
4	紹介	人脈経由でのアプローチ	2025-07-20 03:10:24.167827+00
5	イベント	イベント・セミナーでのアプローチ	2025-07-20 03:10:24.167827+00
\.


--
-- Data for Name: client_companies; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.client_companies (client_company_id, company_name, company_url, contact_person, contact_email, created_at, updated_at) FROM stdin;
1	株式会社人材サービス	https://jinzai-service.co.jp	田中 太郎	tanaka@jinzai-service.co.jp	2025-08-19 14:46:49.269561	2025-08-19 14:46:49.269561
2	グローバル人材株式会社	https://global-jinzai.com	佐藤 花子	sato@global-jinzai.com	2025-08-19 14:46:49.269561	2025-08-19 14:46:49.269561
3	テクノロジー人材センター	https://tech-jinzai.jp	山田 次郎	yamada@tech-jinzai.jp	2025-08-19 14:46:49.269561	2025-08-19 14:46:49.269561
4	HR Solutions Inc.	https://hr-solutions.co.jp	鈴木 美咲	suzuki@hr-solutions.co.jp	2025-08-19 14:46:49.269561	2025-08-19 14:46:49.269561
5	テスト依頼会社	\N	\N	\N	2024-01-01 00:00:00	2025-08-23 01:36:12.434496
6	test	\N	太郎	taro@hoge.jp	2025-09-06 04:29:30.672544	2025-09-06 04:29:30.672544
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.companies (company_id, company_name, company_url, company_address, company_phone, contact_person, contact_email, created_at, updated_at, email_searched, email_search_patterns, confirmed_emails, misdelivery_emails, email_search_memo, headquarters_address, business_status, ap_ng, ap_ng_reason, contact_history, company_memo, operation_memo) FROM stdin;
4	ターゲット会社A		\N	\N	\N	\N	2024-01-01 00:00:00	2025-08-23 01:36:12.555071	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
5	ターゲット会社B		\N	\N	\N	\N	2024-01-01 00:00:00	2025-08-23 01:36:12.64957	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
6	グローバルソリューションズ		\N	\N	\N	\N	2024-01-01 00:00:00	2025-08-23 11:08:21.81049	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
7	イノベーション株式会社		\N	\N	\N	\N	2024-01-01 00:00:00	2025-08-23 11:08:21.868383	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
8	デジタルトランスフォーメーション社		\N	\N	\N	\N	2024-01-01 00:00:00	2025-08-23 11:08:21.946888	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
9	フューチャーシステムズ		\N	\N	\N	\N	2024-01-01 00:00:00	2025-08-23 11:08:22.042173	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
10	アドバンステックコープ		\N	\N	\N	\N	2024-01-01 00:00:00	2025-08-23 11:08:22.122988	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
11	ネクストジェネレーション		\N	\N	\N	\N	2024-01-01 00:00:00	2025-08-23 11:08:22.199251	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
12	スマートインダストリーズ		\N	\N	\N	\N	2024-01-01 00:00:00	2025-08-23 11:08:22.256595	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
13	テクノロジー株式会社		\N	\N	\N	\N	2025-07-20 03:10:24.167827	2025-08-26 10:19:02.226577	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
14	富士通株式会社		\N	\N	\N	\N	2025-08-27 08:22:52.491707	2025-08-27 08:22:52.491707	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
15	株式会社日立製作所		\N	\N	\N	\N	2025-08-27 08:23:10.672059	2025-08-27 08:23:10.672059	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
16	日本電気株式会社		\N	\N	\N	\N	2025-08-27 08:23:34.678091	2025-08-27 08:23:34.678091	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
17	ソフトバンク株式会社		\N	\N	\N	\N	2025-08-27 08:26:29.399019	2025-08-27 08:26:29.399019	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
18	株式会社日立システムズ 		\N	\N	\N	\N	2025-08-27 08:26:34.508338	2025-08-27 08:26:34.508338	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
19	株式会社プロフェッショナルバンク		\N	\N	\N	\N	2025-09-01 20:02:38.992647	2025-09-01 20:02:38.992647	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
20	株式会社テクノロジー		\N	\N	\N	\N	2024-01-01 00:00:00	2025-09-04 06:16:43.184766	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
21	test		\N	\N	\N	\N	2025-09-06 04:29:30.561968	2025-09-06 04:29:30.561968	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
22	株式会社人材サービス	https://jinzai-service.co.jp	\N	\N	田中 太郎	tanaka@jinzai-service.co.jp	2025-08-19 14:46:49.269561	2025-08-19 14:46:49.269561	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
23	グローバル人材株式会社	https://global-jinzai.com	\N	\N	佐藤 花子	sato@global-jinzai.com	2025-08-19 14:46:49.269561	2025-08-19 14:46:49.269561	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
24	テクノロジー人材センター	https://tech-jinzai.jp	\N	\N	山田 次郎	yamada@tech-jinzai.jp	2025-08-19 14:46:49.269561	2025-08-19 14:46:49.269561	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
25	HR Solutions Inc.	https://hr-solutions.co.jp	\N	\N	鈴木 美咲	suzuki@hr-solutions.co.jp	2025-08-19 14:46:49.269561	2025-08-19 14:46:49.269561	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
26	テスト依頼会社		\N	\N			2024-01-01 00:00:00	2025-08-23 01:36:12.434496	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
1	株式会社サンプル	\N	\N	\N	\N	\N	2025-07-20 03:10:24.167827	2025-09-26 21:03:45.274177	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
2	グローバル商事	\N	\N	\N	\N	\N	2025-07-20 03:10:24.167827	2025-09-26 21:04:15.896726	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N
3	GIP株式会社	https://www.gip.co.jp/	\N	\N	\N	\N	2025-07-20 05:00:28.494747	2025-09-26 21:08:57.074413	\N	\N	\N	\N	\N	\N	\N	t	未取引のため	\N	テスト企業メモ	備考です
\.


--
-- Data for Name: priority_levels; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.priority_levels (priority_id, priority_name, priority_value, description, created_at) FROM stdin;
1	最高	5.00	最も重要度が高い	2025-07-20 03:10:24.167827+00
2	高	4.00	重要度が高い	2025-07-20 03:10:24.167827+00
3	中	3.00	標準的な重要度	2025-07-20 03:10:24.167827+00
4	低	2.00	重要度が低い	2025-07-20 03:10:24.167827+00
5	最低	1.00	最も重要度が低い	2025-07-20 03:10:24.167827+00
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.projects (project_id, project_name, status, contract_start_date, contract_end_date, required_headcount, co_manager, re_manager, job_description, requirements, employment_type, position_level, work_location, min_age, max_age, education_requirement, required_qualifications, job_classification, created_at, updated_at, client_company_id) FROM stdin;
4	マーケティングオートメーション導入	OPEN	2024-03-01	2024-09-01	1	佐藤CO	中村RE	MA ツールの導入・設定・運用支援。顧客データ分析とキャンペーン設計を担当。	MA ツール使用経験、Google Analytics、SQL、マーケティング知識	業務委託	\N	東京都千代田区	26	38	\N	\N	\N	2024-01-01 00:00:00+00	2025-08-23 11:08:42.861951+00	3
5	クラウド移行プロジェクト	OPEN	2024-04-01	2024-10-01	2	鈴木CO	渡辺RE	オンプレミス環境からAWSへの移行。インフラ設計・構築・運用の最適化。	AWS 3年以上、Terraform, Docker, Kubernetes経験、Linux	正社員	\N	リモート可	30	50	\N	\N	\N	2024-01-01 00:00:00+00	2025-08-23 11:08:43.07366+00	4
6	モバイルアプリ開発（iOS/Android）	OPEN	2024-05-01	2024-11-01	2	鈴木CO	伊藤RE	小売業向けモバイルアプリの新規開発。ネイティブ開発とUIUX設計。	Swift または Kotlin 2年以上、アプリ公開経験、UI/UX理解	契約社員	\N	リモート可	24	35	\N	\N	\N	2024-01-01 00:00:00+00	2025-08-23 11:08:43.290402+00	5
8	セキュリティ監査・対策実装	OPEN	2024-07-01	2024-01-01	1	田中CO	中村RE	情報セキュリティ監査とペネトレーションテスト。脆弱性対策の実装支援。	セキュリティ監査経験、CISSP/CEH等の資格、ペネトレーションテスト	正社員	\N	リモート可	32	48	\N	\N	\N	2024-01-01 00:00:00+00	2025-08-23 11:08:43.590043+00	2
9	人事システム刷新プロジェクト	IN_PROGRESS	2024-08-01	2024-02-01	2	田中CO	渡辺RE	人事管理システムの要件定義・設計・開発。ワークフロー設計も含む。	Java/C# 3年以上、人事システム経験、要件定義・設計経験	正社員	\N	東京都港区	29	44	\N	\N	\N	2024-01-01 00:00:00+00	2025-08-23 11:08:43.73803+00	3
10	ECサイトリニューアル	IN_PROGRESS	2024-09-01	2024-03-01	3	山田CO	伊藤RE	ECサイトのフロントエンド・バックエンド全面刷新。パフォーマンス改善。	React/Vue.js, Node.js, AWS/GCP, ECサイト開発経験	契約社員	\N	東京都千代田区	26	38	\N	\N	\N	2024-01-01 00:00:00+00	2025-08-23 11:08:43.943244+00	4
11	RPA導入・運用支援	OPEN	2024-10-01	2024-04-01	1	山田CO	中村RE	業務自動化のためのRPAツール導入。業務プロセス分析と自動化設計。	UiPath/WinActor等のRPAツール、業務分析経験、VBA/Python	業務委託	\N	東京都千代田区	28	45	\N	\N	\N	2024-01-01 00:00:00+00	2025-08-23 11:08:44.078726+00	5
1	テスト案件	OPEN	\N	\N	1	\N	\N	\N	\N	\N	\N	\N	28	50	\N	\N	\N	2024-01-01 00:00:00+00	2025-08-23 01:36:12.893861+00	5
2	システム開発案件（金融システム）	OPEN	2024-01-01	2024-07-01	3	田中CO	伊藤RE	金融業界向けの基幹システム開発。Java/Spring Boot を使用した大規模システムの設計・開発を担当。	Java, Spring Boot 3年以上、金融業界経験者優遇、設計書作成経験	正社員	\N	東京都港区	28	45	\N	\N	\N	2024-01-01 00:00:00+00	2025-08-23 11:08:42.480605+00	1
7	データ分析・BI構築プロジェクト	OPEN	2024-06-01	2024-12-01	1	田中CO	高橋RE	売上データの分析基盤構築。Tableau/Power BI を使用したダッシュボード作成。	SQL, Python/R, Tableau/Power BI, 統計学の基礎知識	業務委託	\N	東京都千代田区	27	42	\N	\N	\N	2024-01-01 00:00:00+00	2025-08-23 11:08:43.415484+00	1
3	AI・機械学習システム構築	OPEN	2024-02-01	2024-08-01	2	田中CO	高橋RE	ECサイトの推薦システム開発。Python/TensorFlow を使用した機械学習モデルの構築・運用。	Python, TensorFlow/PyTorch 2年以上、機械学習の実務経験、SQL	契約社員	\N	リモート可	25	40	\N	\N	\N	2024-01-01 00:00:00+00	2025-08-23 11:08:42.715898+00	2
18	test案件	\N	\N	\N	\N	\N	\N		\N	正社員	\N	\N	\N	\N	\N	\N	\N	2025-09-09 10:58:22.86669+00	2025-09-09 10:58:22.86669+00	\N
\.


--
-- Data for Name: company_project_roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.company_project_roles (id, company_id, project_id, role_type, department_name, priority_id, classification, is_active, notes, created_at, updated_at) FROM stdin;
1	2	4	target	営業	1	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
2	3	5	target	人事	1	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
3	20	6	target	開発	1	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
4	1	8	target	あああ	1	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
5	10	9	target	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
6	4	9	target	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
7	1	10	target	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
8	3	10	target	営業	1	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
9	6	11	target	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
10	2	1	target	開発	1	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
11	5	2	target	リモート可	5	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
12	20	7	target	テック	4	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
13	20	3	target	テクノ	1	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
14	3	3	target	人材	1	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
15	9	3	target	開発	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
16	24	4	client	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
17	25	5	client	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
18	26	6	client	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
19	23	8	client	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
20	24	9	client	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
21	25	10	client	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
22	26	11	client	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
23	26	1	client	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
24	22	2	client	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
25	22	7	client	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
26	23	3	client	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
27	1	18	client	\N	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
28	5	18	target	開発部門	\N	\N	t	\N	2025-09-27 14:11:20.610223+00	2025-09-27 14:11:20.610223+00
29	4	4	target	開発	\N	\N	t	\N	2025-10-04 03:18:09.075024+00	2025-10-04 03:18:09.075024+00
31	3	4	target	開発	\N	\N	t	\N	2025-10-04 03:25:38.353901+00	2025-10-04 03:25:38.353901+00
\.


--
-- Data for Name: search_assignees; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.search_assignees (assignee_id, assignee_name, created_at, updated_at) FROM stdin;
1	田中	2025-07-20 03:10:24.167827+00	2025-07-20 03:10:24.167827+00
2	佐藤	2025-07-20 03:10:24.167827+00	2025-07-20 03:10:24.167827+00
3	高橋	2025-07-20 03:10:24.167827+00	2025-07-20 03:10:24.167827+00
4	山田	2025-07-20 03:10:24.167827+00	2025-07-20 03:10:24.167827+00
\.


--
-- Data for Name: target_companies; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.target_companies (target_company_id, company_name, created_at, updated_at, email_searched, linkedin_searched, homepage_searched, eight_search, keyword_searches, other_searches, company_url, email_search_patterns, confirmed_emails, misdelivery_emails, email_search_memo, classification, target_department) FROM stdin;
3	グローバル商事	2025-07-20 03:10:24.167827+00	2025-08-29 14:06:20.17413+00	\N	\N	\N	\N	\N	\N	\N	["@global.marchant.jp1", "@global.marchant.jp2", "@global.marchant.jp3", "@global.marchant.jp5", "@global.marchant.jp4", "@global.marchant.jp6"]	[{"name": "aaaaa", "email": "test@hoge.jp", "position": "", "department": "", "confirmed_date": "2025-08-29", "confirmation_method": "LinkedIn"}, {"name": "name", "email": "aaaa@hoge.jp", "position": "部長", "department": "test div", "confirmed_date": "2025-08-29", "confirmation_method": "名刺交換"}]	[{"memo": "", "email": "fail@hoge.jp", "reason": "同姓同名の別人", "sent_date": "2025-08-29"}, {"memo": "aaaa", "email": "fail2@hoges.jp", "reason": "その他", "sent_date": "2025-08-29"}]	\N	\N	\N
5	ターゲット会社A	2024-01-01 00:00:00+00	2025-08-23 01:36:12.555071+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6	ターゲット会社B	2024-01-01 00:00:00+00	2025-08-23 01:36:12.64957+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
8	グローバルソリューションズ	2024-01-01 00:00:00+00	2025-08-23 11:08:21.81049+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9	イノベーション株式会社	2024-01-01 00:00:00+00	2025-08-23 11:08:21.868383+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
10	デジタルトランスフォーメーション社	2024-01-01 00:00:00+00	2025-08-23 11:08:21.946888+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
11	フューチャーシステムズ	2024-01-01 00:00:00+00	2025-08-23 11:08:22.042173+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
12	アドバンステックコープ	2024-01-01 00:00:00+00	2025-08-23 11:08:22.122988+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
13	ネクストジェネレーション	2024-01-01 00:00:00+00	2025-08-23 11:08:22.199251+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
14	スマートインダストリーズ	2024-01-01 00:00:00+00	2025-08-23 11:08:22.256595+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2	テクノロジー株式会社	2025-07-20 03:10:24.167827+00	2025-08-26 10:19:02.226577+00	\N	\N	\N	\N	\N	\N	\N	["こんにちは"]	[{"name": "aaa", "email": "akira.fujita@gmail.com", "position": "hoge", "department": "bb", "confirmed_date": "2025-08-26", "confirmation_method": "LinkedIn"}, {"name": "aaa", "email": "akira.fujita@gmail.com", "position": "", "department": "bb", "confirmed_date": "2025-08-26", "confirmation_method": "LinkedIn"}]	\N	\N	\N	\N
15	富士通株式会社	2025-08-27 08:22:52.491707+00	2025-08-27 08:22:52.491707+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
17	株式会社日立製作所	2025-08-27 08:23:10.672059+00	2025-08-27 08:23:10.672059+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
18	日本電気株式会社	2025-08-27 08:23:34.678091+00	2025-08-27 08:23:34.678091+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
19	ソフトバンク株式会社	2025-08-27 08:26:29.399019+00	2025-08-27 08:26:29.399019+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
20	株式会社日立システムズ 	2025-08-27 08:26:34.508338+00	2025-08-27 08:26:34.508338+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
21	株式会社プロフェッショナルバンク	2025-09-01 20:02:38.992647+00	2025-09-01 20:02:38.992647+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7	株式会社テクノロジー	2024-01-01 00:00:00+00	2025-09-04 06:16:43.184766+00	\N	\N	\N	\N	\N	\N	\N	["tech-a.jp", "tech-b.jp"]	[{"name": "テストデータ", "email": "test-taro@tech.jp", "position": "", "department": "", "confirmed_date": "2025-09-04", "confirmation_method": "LinkedIn"}]	\N	\N	\N	\N
23	test	2025-09-06 04:29:30.561968+00	2025-09-06 04:29:30.561968+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1	株式会社サンプル	2025-07-20 03:10:24.167827+00	2025-10-04 11:51:22.673417+00	\N	\N	\N	\N	[{"date": "2025-10-04", "query": "python エンジニア　募集", "keyword": "python", "search_number": 1}]	\N	\N	\N	\N	\N	\N	\N	\N
4	GIP株式会社	2025-07-20 05:00:28.494747+00	2025-10-04 14:09:11.046384+00	\N	2025-10-04	2025-10-04	2025-10-04	[{"date": "2025-10-04", "query": "pyhton 転職", "keyword": "pythonエンジニア", "search_number": 1}, {"date": "2025-10-04", "query": "python 転職　年収", "keyword": "pythonエンジニア", "search_number": 2}]	[{"date": "2025-10-04", "method": "マイナビ検索", "search_number": 1}]	\N	["hoge@gip.jp", "hogehoge@gip.jp"]	[{"name": "hoge 太郎", "email": "hogetarou@gip.co.jp", "position": "", "department": "", "confirmed_date": "2025-10-04", "confirmation_method": "LinkedIn"}]	[{"memo": "", "email": "hoge@gip.com", "reason": "会社間違い", "sent_date": "2025-10-04"}]	\N	\N	\N
\.


--
-- Data for Name: contacts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.contacts (contact_id, target_company_id, full_name, furigana, estimated_age, profile, url, screening_status, primary_screening_comment, priority_id, name_search_key, work_comment, search_assignee_id, search_date, email_address, created_at, updated_at, department_name, position_name, last_name, first_name, furigana_last_name, furigana_first_name, birth_date, actual_age, company_id) FROM stdin;
13	1	test taro	\N	45.0	\N	\N	実施済み	\N	2	\N	\N	1	\N	test-taro@sample-it.co.jp	2025-09-20 11:25:54.983658+00	2025-09-20 11:25:54.983678+00	\N	\N	\N	\N	\N	\N	\N	\N	\N
1	1	山田 太郎	ヤマ ダタロウ	40代	人事部長として10年の経験	\N	\N	\N	1	\N	2025-09-20 案件についての返信あり	1	2024-01-15	\N	2025-07-20 03:10:24.167827+00	2025-09-20 02:34:48.90441+00	人事部	部長	山田	太郎	ヤマ	ダタロウ	\N	\N	1
14	5	最小太郎	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	minimal@example.com	2025-09-20 11:25:55.438834+00	2025-09-28 12:40:57.075889+00	\N	\N	\N	\N	\N	\N	\N	\N	4
4	3	鈴木 三郎	スズ キサブロウ	45歳	管理部主任	\N	\N	\N	3	\N	\N	3	2024-01-18	\N	2025-07-20 03:10:24.167827+00	2025-09-06 04:54:21.298909+00	管理部	主任	鈴木	三郎	スズ	キサブロウ	2025-08-20	44	2
7	4	原田 雅志	ハラダ マサシ	40歳前後	テスト	\N	\N	\N	2	\N	\N	\N	\N	\N	2025-09-01 19:48:33.863461+00	2025-09-06 04:54:21.298909+00	HRコンサルティング事業部　リサーチ部門	マネージャー	原田	雅志	ハラダ	マサシ	\N	\N	3
3	2	田中 次郎	タナ カジロウ	35歳	エンジニアリングマネージャー	\N	\N	\N	1	\N	\N	1	2024-01-17	\N	2025-07-20 03:10:24.167827+00	2025-09-06 04:54:21.298909+00	開発部第二課	マネージャー	田中	次郎	タナ	カジロウ	\N	\N	13
5	15	松本 潤	マツモト ジュン	30代後半（写真より）	▼以下、HPより\nプロフィール■入社以来、ソフトウェア開発に従事。\n現在は、プロジェクトマネージャー。\n\n読み■マツモト　ジュン\n	写真あり■https://~~	\N	\N	\N	\N	\N	\N	2025-08-28	\N	2025-08-27 08:33:58.760777+00	2025-09-06 04:54:21.298909+00	\N	\N	松本	潤	マツモト	ジュン	\N	\N	14
\.


--
-- Data for Name: contact_approaches; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.contact_approaches (approach_id, contact_id, approach_date, approach_method_id, approach_order, created_at, notes) FROM stdin;
3	1	2025-09-01	1	3	2025-09-20 01:10:13.634106+00	\N
7	1	2025-09-20	2	2	2025-09-20 01:20:07.740026+00	っっg
8	1	2025-09-03	1	1	2025-09-20 01:22:03.860087+00	メールにて案件をお伝えした。
9	5	2025-09-24	2	1	2025-09-24 09:48:13.345986+00	電話
10	5	2025-09-02	1	2	2025-09-24 09:48:24.44543+00	メールで連絡
\.


--
-- Data for Name: manager_types; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.manager_types (type_id, type_code, type_name, created_at, updated_at) FROM stdin;
1	CO	案件調整担当	2025-09-09 11:58:04.985817+00	2025-09-09 11:58:04.985817+00
2	RE	採用担当	2025-09-09 11:58:04.985817+00	2025-09-09 11:58:04.985817+00
3	Sales	営業担当	2025-09-09 11:58:04.985817+00	2025-09-09 11:58:04.985817+00
4	PM	PM・進行管理	2025-09-09 11:58:04.985817+00	2025-09-09 11:58:04.985817+00
\.


--
-- Data for Name: project_assignments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_assignments (assignment_id, project_id, contact_id, assignment_status, created_at, updated_at) FROM stdin;
2	3	1	採用決定	2025-09-04 08:54:16.251384+00	2025-09-04 08:54:16.251384+00
6	3	7	面談中	2025-09-15 01:56:42.967851+00	2025-09-15 01:56:42.967851+00
8	3	13	採用決定	2025-09-28 13:09:15.128553+00	2025-09-28 13:09:15.128553+00
\.


--
-- Data for Name: project_companies; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_companies (id, project_id, company_id, role, department_name, priority_id, created_at) FROM stdin;
1	4	2	target	営業	1	2025-09-06 04:52:15.975279
2	5	3	target	人事	1	2025-09-06 04:52:15.975279
3	6	20	target	開発	1	2025-09-06 04:52:15.975279
4	8	1	target	あああ	1	2025-09-06 04:52:15.975279
5	9	10	target	\N	\N	2025-09-06 04:52:15.975279
6	9	4	target	\N	\N	2025-09-06 04:52:15.975279
7	10	1	target	\N	\N	2025-09-06 04:52:15.975279
8	10	3	target	営業	1	2025-09-06 04:52:15.975279
9	11	6	target	\N	\N	2025-09-06 04:52:15.975279
10	1	2	target	開発	1	2025-09-06 04:52:15.975279
11	2	5	target	リモート可	5	2025-09-06 04:52:15.975279
12	7	20	target	テック	4	2025-09-06 04:52:15.975279
13	3	20	target	テクノ	1	2025-09-06 04:52:15.975279
14	3	3	target	人材	1	2025-09-06 04:52:15.975279
15	3	9	target	開発	\N	2025-09-06 04:52:15.975279
16	4	24	client	\N	\N	2025-09-06 04:52:15.975279
17	5	25	client	\N	\N	2025-09-06 04:52:15.975279
18	6	26	client	\N	\N	2025-09-06 04:52:15.975279
19	8	23	client	\N	\N	2025-09-06 04:52:15.975279
20	9	24	client	\N	\N	2025-09-06 04:52:15.975279
21	10	25	client	\N	\N	2025-09-06 04:52:15.975279
22	11	26	client	\N	\N	2025-09-06 04:52:15.975279
23	1	26	client	\N	\N	2025-09-06 04:52:15.975279
24	2	22	client	\N	\N	2025-09-06 04:52:15.975279
25	7	22	client	\N	\N	2025-09-06 04:52:15.975279
26	3	23	client	\N	\N	2025-09-06 04:52:15.975279
39	18	1	client	\N	\N	2025-09-09 10:58:22.933632
40	18	5	target	開発部門	\N	2025-09-09 10:58:23.022061
\.


--
-- Data for Name: project_managers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_managers (id, project_id, manager_type_code, name, email, phone, is_primary, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: project_target_companies; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_target_companies (id, project_id, target_company_id, created_at, updated_at, department_name, priority_id) FROM stdin;
18	4	3	2025-08-27 01:07:17.302917+00	2025-08-27 01:07:17.302917+00	営業	1
19	5	4	2025-08-27 01:07:49.023144+00	2025-08-27 01:07:49.023144+00	人事	1
20	6	7	2025-08-27 01:13:45.656569+00	2025-08-27 01:13:45.656569+00	開発	1
21	8	1	2025-08-27 01:14:48.488351+00	2025-08-27 01:14:48.488351+00	あああ	1
22	9	12	2025-08-27 01:19:09.805633+00	2025-08-27 01:19:09.805633+00	\N	\N
23	9	5	2025-08-27 01:19:09.869925+00	2025-08-27 01:19:09.869925+00	\N	\N
25	10	1	2025-08-27 01:27:47.589429+00	2025-08-27 01:27:47.589429+00	\N	\N
26	10	4	2025-08-27 01:27:47.653981+00	2025-08-27 01:27:47.653981+00	営業	1
27	11	8	2025-08-27 01:31:09.102186+00	2025-08-27 01:31:09.102186+00	\N	\N
28	1	3	2025-08-27 01:36:31.167888+00	2025-08-27 01:36:31.167888+00	開発	1
29	2	6	2025-08-27 01:37:07.126094+00	2025-08-27 01:37:07.126094+00	リモート可	5
32	7	7	2025-08-27 02:18:07.05586+00	2025-08-27 02:18:07.05586+00	テック	4
38	3	7	2025-08-27 08:45:29.944099+00	2025-08-27 08:45:29.944099+00	テクノ	1
39	3	4	2025-08-27 08:45:30.095972+00	2025-08-27 08:45:30.095972+00	人材	1
40	3	11	2025-08-27 08:45:30.243972+00	2025-08-27 08:45:30.243972+00	開発	\N
41	4	4	2025-09-24 10:08:24.735332+00	2025-09-24 10:08:24.735332+00	開発部	\N
42	4	6	2025-09-24 10:08:56.88837+00	2025-09-24 10:08:56.88837+00	開発部	\N
\.


--
-- Data for Name: work_locations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.work_locations (work_location_id, contact_id, postal_code, work_address, building_name, created_at, updated_at) FROM stdin;
\.


--
-- Name: addresses_address_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.addresses_address_id_seq', 1, false);


--
-- Name: approach_methods_method_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.approach_methods_method_id_seq', 5, true);


--
-- Name: client_companies_client_company_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.client_companies_client_company_id_seq', 6, true);


--
-- Name: companies_company_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.companies_company_id_seq', 26, true);


--
-- Name: company_project_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.company_project_roles_id_seq', 31, true);


--
-- Name: contact_approaches_approach_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.contact_approaches_approach_id_seq', 10, true);


--
-- Name: contacts_contact_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.contacts_contact_id_seq', 14, true);


--
-- Name: manager_types_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.manager_types_type_id_seq', 4, true);


--
-- Name: priority_levels_priority_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.priority_levels_priority_id_seq', 5, true);


--
-- Name: project_assignments_assignment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_assignments_assignment_id_seq', 8, true);


--
-- Name: project_companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_companies_id_seq', 40, true);


--
-- Name: project_managers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_managers_id_seq', 1, false);


--
-- Name: project_target_companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_target_companies_id_seq', 42, true);


--
-- Name: projects_project_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.projects_project_id_seq', 18, true);


--
-- Name: search_assignees_assignee_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.search_assignees_assignee_id_seq', 4, true);


--
-- Name: target_companies_target_company_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.target_companies_target_company_id_seq', 23, true);


--
-- PostgreSQL database dump complete
--

\unrestrict lcmtBTNDf31Pj2fJVt5h55Nv0TCFmzam6uvQt7otGQV5CcsaxJAU3jVaD61QnnS

