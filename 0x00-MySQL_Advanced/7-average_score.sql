-- script that creates a stored procedure ComputeAverageScoreForUser that computes and store the average score for a student. Note: An average score can be a decimal
-- Requirements:
--     Procedure ComputeAverageScoreForUser is taking 1 input:
--         user_id, a users.id value (you can assume user_id is linked to an existing users)

DELIMITER $$
CREATE PROCEDURE ComputeAverageScoreForUser(IN user_id INT)
BEGIN
	DECLARE total_score FLOAT DEFAULT 0;
	DECLARE total_projects INT DEFAULT 0;
	SELECT SUM(score), COUNT(*)
		INTO total_score, total_projects
		FROM corrections
		WHERE corrections.user_id = user_id;
	UPDATE users
		SET average_score = total_score / total_projects
		WHERE id = user_id;
END$$
DELIMITER ;
