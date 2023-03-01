CREATE DATABASE tp6;

USE tp6;

CREATE TABLE IF NOT EXISTS `vj_group`(
	`group_id` INT NOT NULL COMMENT 'group id(主键)',
    `group_name` VARCHAR(255) NOT NULL COMMENT 'group名称',
	PRIMARY KEY(`group_id`)
);

CREATE TABLE if NOT EXISTS `vj_contest`(
	`contest_id` INT NOT NULL COMMENT '比赛id(主键)',
	`contest_name` VARCHAR(255) NOT NULL COMMENT '比赛名称',
	`group_id` INT NOT NULL COMMENT '所属group的id',
    `begin_time` INT NOT NULL COMMENT '比赛开始时间戳',
    `end_time` INT NOT NULL COMMENT '比赛结束时间戳',
    `last_time` INT NOT NULL DEFAULT(0) COMMENT '上次爬取的时间戳',
    `penalty` INT NOT NULL DEFAULT(0) COMMENT '错误提交的罚时（单位：秒）',
    `sum_time` BOOL NOT NULL DEFAULT(false) COMMENT '罚时计算方式（true为计算和，false为计算最后一次提交）',
	PRIMARY KEY(`contest_id`)
);

CREATE TABLE if NOT EXISTS `vj_contest_problem` (
	`problem_id` INT AUTO_INCREMENT COMMENT '题目id(主键)',
	`contest_id` INT NOT NULL COMMENT '所属比赛id',
    `problem_no` INT NOT NULL COMMENT '题号',
    PRIMARY KEY(`problem_id`)
);

CREATE TABLE if NOT EXISTS `vj_contest_result` (
	`problem_id` INT AUTO_INCREMENT COMMENT '题目id',
    `user_id` INT NOT NULL COMMENT '用户id',
    `attempted_time` INT NOT NULL COMMENT '提交次数',
    `is_solved` INT NOT NULL COMMENT '是否通过(1：通过/0：未通过)',
    `solved_time` INT NOT NULL COMMENT '通过时间戳',
    PRIMARY KEY(`problem_id`)
);

CREATE TABLE if NOT EXISTS `vj_submission`(
	`submission_id` int AUTO_INCREMENT COMMENT '提交id(主键)',
	`contest_id` INT NOT NULL COMMENT '提交比赛id',
	`user_id` INT NOT NULL COMMENT '提交的用户id',
    `problem_id` INT NOT NULL COMMENT '提交的题目id',
    `submit_time` INT NOT NULL COMMENT '提交时间戳',
    `is_accepted` INT NOT NULL COMMENT '是否正确(1：正确/0：未正确)',
	PRIMARY KEY(`submission_id`)
);

CREATE TABLE if NOT EXISTS `vj_user` (
	`user_id` INT NOT NULL COMMENT '用户id',
    `group_id` INT NOT NULL COMMENT 'group id',
    `user_name` VARCHAR(255) NOT NULL COMMENT '用户名',
    `user_nickname` VARCHAR(255) NOT NULL COMMENT '用户昵称',
    PRIMARY KEY(`user_id`,`group_id`)
);
