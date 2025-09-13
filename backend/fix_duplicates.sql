-- Fix duplicate quiz results by keeping only the latest submission for each user-challenge pair

-- First add the updated_at column manually
ALTER TABLE quiz_result ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

-- Update the new column with submitted_at values for existing records
UPDATE quiz_result SET updated_at = submitted_at WHERE updated_at IS NULL;

-- Remove duplicates, keeping only the most recent submission for each user-challenge pair
WITH duplicates AS (
    SELECT id, 
           ROW_NUMBER() OVER (
               PARTITION BY user_id, challenge_id 
               ORDER BY submitted_at DESC, id DESC
           ) as rn
    FROM quiz_result
)
DELETE FROM quiz_result 
WHERE id IN (
    SELECT id FROM duplicates WHERE rn > 1
);

-- Now add the unique constraint
ALTER TABLE quiz_result ADD CONSTRAINT unique_user_challenge_result UNIQUE (user_id, challenge_id);

-- Show remaining records
SELECT user_id, challenge_id, COUNT(*) as count 
FROM quiz_result 
GROUP BY user_id, challenge_id 
HAVING COUNT(*) > 1;