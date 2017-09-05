#!/bin/bash
 
     echo "start copy file .."
         find  ../output -name  "*.txt" | xargs cat > sum.txt
             echo "done !"
