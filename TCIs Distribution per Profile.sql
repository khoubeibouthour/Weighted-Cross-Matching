select distinct name, label, count(name) from comparisons, profiles where profile_id = profile and face_recog <= .65 group by name, label order by name;
select distinct name, label, count(name) from comparisons, profiles where profile_id = profile and face_recog > 1.67 group by name, label order by name;