dating-server:
	$(TROUPE)/bin/troupec dating-server.trp -o ./out/dating-server.js
	node $(TROUPE)/rt/built/troupe.js -f=./out/dating-server.js --id=../ids/id-server.json --trustmap=../trustmaps/GoT.json --aliases=aliases.json

dating-client-mj:
	$(TROUPE)/bin/troupec dating-client-mj.trp -o ./out/dating-client-mj.js
	node $(TROUPE)/rt/built/troupe.js -f=./out/dating-client-mj.js --id=../ids/id-mj.json --trustmap=../trustmaps/client.json --aliases=aliases.json

dating-client-peter:
	$(TROUPE)/bin/troupec dating-client-peter.trp -o ./out/dating-client-peter.js
	node $(TROUPE)/rt/built/troupe.js -f=./out/dating-client-peter.js --id=../ids/id-peter.json --trustmap=../trustmaps/client.json --aliases=aliases.json