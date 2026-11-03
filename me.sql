-- The work, skills and current focus on this profile are drawn from this file.
-- sqlite3 me.db < me.sql
-- sqlite3 me.db "SELECT label, what FROM now"

CREATE TABLE engineer (
  id    INTEGER PRIMARY KEY,
  name  TEXT NOT NULL,
  role  TEXT NOT NULL,
  city  TEXT NOT NULL,
  intro TEXT NOT NULL
);

CREATE TABLE work (
  id    INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  what  TEXT NOT NULL
);

CREATE TABLE skill (
  id   INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL
);

CREATE TABLE now (
  id    INTEGER PRIMARY KEY,
  label TEXT NOT NULL,
  what  TEXT NOT NULL
);

INSERT INTO engineer VALUES (1, 'Ashutosh Anand', 'Backend engineer', 'New Delhi',
  'I build APIs, integrations, data pipelines and background jobs. The stack follows the project, and strong fundamentals and AI tooling help me learn new tech fast.');

INSERT INTO work VALUES
  (1, 'Connection pool exhaustion', 'Each summary call fanned out 16 to 24 queries and starved the pool, so I cut it to 2: 1 connection, not 10.'),
  (2, 'Large write batching', 'Batched writes so big runs never hold long transactions: about 45 s to under 1 s at 300,000 rows, 25 to 35% faster.'),
  (3, 'Caching pipeline revamp', 'Phased, concurrent pulls cut a 1M record reload from 215 s to 69 s; 10 pulls now use about the CPU and RAM 5 used to.'),
  (4, 'Hierarchical auto-sync', 'Auto-syncs parent-child records at any depth: changes and removals cascade to all descendants, never upward.'),
  (5, 'SQS to BullMQ migration', 'Moved for more control, and built the job orchestrator that decides which job runs and which queues.'),
  (6, 'EV charging protocol integration', 'So charging networks connect without manual setup: OCPI client with automated credentials and remote commands.'),
  (7, 'Payment reversal', 'Lets a payment be rolled back cleanly on an EV charging platform through a reverse transaction, with an audit trail.'),
  (8, 'AI engineering setup', 'Written rules get forgotten, so 84 hooks and 30+ skills enforce mine in Claude Code at the moment of action.');

INSERT INTO skill (name, kind) VALUES
  ('TypeScript', 'Languages'), ('JavaScript', 'Languages'), ('Python', 'Languages'), ('Rust', 'Languages'), ('Go', 'Languages'), ('Dart', 'Languages'), ('Java', 'Languages'), ('C++', 'Languages'),
  ('Node.js', 'Backend'), ('Express', 'Backend'), ('AdonisJS', 'Backend'), ('Hono', 'Backend'), ('Django', 'Backend'), ('FastAPI', 'Backend'), ('GraphQL', 'Backend'), ('Drizzle', 'Backend'), ('Sequelize', 'Backend'), ('BullMQ', 'Backend'),
  ('PostgreSQL', 'Data'), ('Redis', 'Data'), ('Supabase', 'Data'), ('MySQL', 'Data'), ('MongoDB', 'Data'), ('DocumentDB', 'Data'),
  ('AWS S3', 'Cloud'), ('Lambda', 'Cloud'), ('SQS', 'Cloud'), ('SNS', 'Cloud'), ('EventBridge', 'Cloud'), ('Step Functions', 'Cloud'), ('CloudFront', 'Cloud'), ('Cloudflare Workers', 'Cloud'), ('Docker', 'Cloud'),
  ('Salesforce', 'Integrations'), ('Salesloft', 'Integrations'), ('Freshworks', 'Integrations'), ('Zoho Projects', 'Integrations'), ('OCPI', 'Integrations'), ('Enterprise HR and middleware APIs', 'Integrations'),
  ('React', 'Frontend'), ('Vite', 'Frontend'), ('Tailwind', 'Frontend'), ('Flutter', 'Frontend'),
  ('Claude Code', 'AI and tools'), ('MCP', 'AI and tools'), ('FFmpeg', 'AI and tools'), ('OpenCV', 'AI and tools'), ('Git', 'AI and tools'), ('Linux', 'AI and tools'), ('Bash', 'AI and tools'), ('GitHub Actions', 'AI and tools');

INSERT INTO now VALUES
  (1, 'At work', 'Connecting enterprise systems so HR data moves reliably between them.'),
  (2, 'My setup', 'Refining how I work with Claude Code, so a repeated mistake gets caught and fixed automatically.'),
  (3, 'Building', 'Small, lightweight native tools in Rust.');
