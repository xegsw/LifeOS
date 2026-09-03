CREATE TABLE context_item (
  id TEXT PRIMARY KEY,
  domain TEXT NOT NULL,
  authorized INTEGER NOT NULL,
  status TEXT NOT NULL,
  expires_at_ms INTEGER,
  created_at_ms INTEGER NOT NULL
);
INSERT INTO context_item VALUES ('c3-work-valid','work',1,'active',NULL,10);
INSERT INTO context_item VALUES ('c3-health-valid','health',1,'active',NULL,20);
INSERT INTO context_item VALUES ('c3-work-unauthorized','work',0,'active',NULL,30);
INSERT INTO context_item VALUES ('c3-health-expired','health',1,'active',1,40);
INSERT INTO context_item VALUES ('c3-work-revoked','work',1,'revoked',NULL,50);
SELECT id, domain FROM context_item
 WHERE authorized=1 AND status='active' AND (expires_at_ms IS NULL OR expires_at_ms>100)
 ORDER BY created_at_ms ASC, id ASC;
