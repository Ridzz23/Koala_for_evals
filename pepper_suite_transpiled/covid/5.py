import sys

y = sed "s/T\\(..\\):..:../,\\1/" sys.argv[1] $| awk "-F," f"
!seen[{sys.argv[1]} {sys.argv[2]} {sys.argv[4]}] { seen[{sys.argv[1]} {sys.argv[2]} {sys.argv[4]}] = 1; hours[{sys.argv[1]} {sys.argv[4]}]++; bus[{sys.argv[4]}] = 1; day[{sys.argv[1]}] = 1; }
END {
   PROCINFO["sorted_in"] = "@ind_str_asc"
   for (d in day)
     printf("\t%s", d);
   printf("\n");
   for (b in bus) {
     printf("%s", b);
     for (d in day)
       printf("\t%s", hours[d b]);
     printf("\n");
   }
}"
print(y)