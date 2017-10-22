#include <stdio.h>
#include <sys/socket.h> /* for socket() and bind() */
#include <arpa/inet.h>  /* for sockaddr_in */
#include <stdlib.h>     /* for exit() */
#include <string.h>     /* for memset() */
#include <unistd.h>     /* for sleep() */
#include <time.h>
#include <queue>
#include <string>

using namespace std;

#define PORT 50000
#define MAXRECVSTRING 100

struct Packet
{
    string message;
    time_t time;
};

int main(int argc, char *argv[])
{
    int sock;                         /* Socket */
    struct sockaddr_in broadcastAddr; /* Broadcast Address */

    queue<Packet> S1, S2, S3;
    char recvString[MAXRECVSTRING + 1];
    int recvStringLen;

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

    while(1)
    {
        while(1)
        {
            Packet p;

            /* Receive a datagram from a source */
            if ((recvStringLen = recvfrom(sock, recvString, MAXRECVSTRING, MSG_DONTWAIT | MSG_PEEK, NULL, 0)) <= 0)
                break;
            recvString[recvStringLen] = '\0';

            // p.message(recvString);
        }

        printf("Received: %s\n", recvString);    /* Print the received string */
    }
    
    close(sock);
    exit(0);
}