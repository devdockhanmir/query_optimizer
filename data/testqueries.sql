-- Single table filter
SELECT * FROM R WHERE col1 < 15;

-- Two-table join with equi-join
SELECT * FROM R, S WHERE R.col1 = S.colA;

-- Two-table join with filter
SELECT * FROM R, S WHERE R.col1 = S.colA AND R.col2 < 250;
