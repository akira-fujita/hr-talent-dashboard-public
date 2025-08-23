-- Change search columns from boolean to date type in companies table
ALTER TABLE companies 
  ALTER COLUMN homepage_searched TYPE DATE USING CASE WHEN homepage_searched = true THEN CURRENT_DATE ELSE NULL END,
  ALTER COLUMN eight_search TYPE DATE USING CASE WHEN eight_search = true THEN CURRENT_DATE ELSE NULL END,
  ALTER COLUMN linkedin_searched TYPE DATE USING CASE WHEN linkedin_searched = true THEN CURRENT_DATE ELSE NULL END,
  ALTER COLUMN keyword_searched TYPE DATE USING CASE WHEN keyword_searched = true THEN CURRENT_DATE ELSE NULL END;