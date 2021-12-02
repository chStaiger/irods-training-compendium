#Bunny Hunt

imkdir game2
IHOME=/aliceZone/home/alice

iput bunny.txt
iput test1.txt game2/file1.txt --metadata "GAME; Only 7; days"
iput test4.txt game2/file2.txt --metadata "GAME; until; Easter, "
iput test5.txt game2/file3.txt --metadata "GAME; download bunny here:; /aliceZone/home/alice/bunny.txt"

ichmod -r read public game2
ichmod read public $IHOME
ichmod read public $IHOME/bunny.txt

ils -A $IHOME/bunny.txt
ils -Ar $IHOME/game2

#Halloween

imkdir game
iput test1.txt game/test1.txt --metadata "move three down; scary: do not open; GAME"
iput test2.txt game/test2.txt --metadata "move; three down: too early; do not open; GAME"
iput test3.txt game/test3.txt --metadata "Look inside; Congratulations open me; GAME"
iput test4.txt game/test4.txt --metadata "move up; but where? too late .... do not open; GAME"
iput test5.txt game/test5.txt --metadata "move two; up ... way too late... do not open; GAME"
iput test6.txt game/test6.txt --metadata "move two up; way too late - do not open; GAME did you try 'move', 'early' or 'late'"

ichmod -r read public game
