#include <cstdio>
#include <sys/socket.h> /* for socket() and bind() */
#include <arpa/inet.h>  /* for sockaddr_in */
#include <stdlib.h>     /* for exit() */
#include <string.h>     /* for memset() */
#include <unistd.h>     /* for sleep() */
#include <time.h>
#include <cstring>

using namespace std;

#define PORT 50001
#define MAXRECVSTRING 100

int main(int argc, char *argv[])
{
    int sock;                         /* Socket */
    struct sockaddr_in broadcastAddr; /* Broadcast Address */

    /* Create a best-effort datagram socket using UDP */
    if ((sock = socket(PF_INET, SOCK_DGRAM, IPPROTO_UDP)) < 0)
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    /* Construct bind structure */
    memset(&broadcastAddr, 0, sizeof(broadcastAddr));   /* Zero out structure */
    broadcastAddr.sin_family = AF_INET;                 /* Internet address family */
    broadcastAddr.sin_addr.s_addr = htonl(INADDR_ANY);  /* Any incoming interface */
    broadcastAddr.sin_port = htons(PORT);               /* Broadcast port */

    /* Bind to the broadcast port */
    if (bind(sock, (struct sockaddr *) &broadcastAddr, sizeof(broadcastAddr)) < 0)
    {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    char recvString[MAXRECVSTRING + 1];
    int recvStringLen;

    int count = 0;

    while(1)
    {
        if ((recvStringLen = recvfrom(sock, recvString, MAXRECVSTRING, 0, NULL, 0)) < 0)
        {
            perror("recvfrom failed");
            exit(EXIT_FAILURE);
        }
        
        switch(recvString[0])
        {
            case '1':
                printf("S1\n");
                break;

            case '2':
                printf("S2\n");
                break;

            case '3':
                printf("S3\n");
                break;

            default:
                continue;
        }
    }
    
    close(sock);
    exit(0);
}