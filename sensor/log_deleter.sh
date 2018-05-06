


cowrie_deleter(){
    rm -rf /data/cowrie/log/cowrie.json.*
}

glastopf_deleter(){
    truncate -s 0 /data/glastopf/log/glastopf.log
}

dionaea_deleter(){
    truncate -s 0 /data/dionaea/dionaea-errors.log
    truncate -s 0 /data/dionaea/dionaea.json
    rm -rf /data/dionaea/binaries/*
}


main(){
    cowrie_deleter
    dionaea_deleter
    glastopf_deleter
}

main