#include <cstdio>
#include <sys/socket.h> /* for socket() and bind() */
#include <arpa/inet.h>  /* for sockaddr_in */
#include <stdlib.h>     /* for exit() */
#include <string.h>     /* for memset() */
#include <unistd.h>     /* for sleep() */
#include <time.h>
#include <queue>
#include <cstring>

using namespace std;

#define PORT 50000
#define SENDPORT 50001
#define MAXRECVSTRING 100

void sendMessage(char *message, int messageLen)
{
    int server_fd;                          /* Socket File Descriptor */
    int opt = 1;                            /* Socket opt to set permission to broadcast */
    struct sockaddr_in broadcastAddress;    /* Broadcast address sockaddr_in - references elements 
                                            of the socket address. "in" for internet */
    char *broadcastIP = "127.255.255.255";  /* Broadcast IP address */

    /* Create socket for sending datagrams */
    if ((server_fd = socket(PF_INET, SOCK_DGRAM, IPPROTO_UDP)) < 0) /* creates socket, SOCK_STREAM is for TCP. SOCK_DGRAM for UDP */
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    /* Set socket to allow broadcast */
    if (setsockopt(server_fd, SOL_SOCKET, SO_BROADCAST, /* SOL_SOCKET is the socket layer itself */
                        (void *) &opt, sizeof(opt)) < 0)
    {
        perror("setsockopt failed");
        exit(EXIT_FAILURE);
    }

    memset(&broadcastAddress, 0, sizeof(broadcastAddress));
    broadcastAddress.sin_family = AF_INET;                      /* Internet address family. For IPv6, it's AF_INET6. 29 others exist like AF_UNIX etc.  */
    broadcastAddress.sin_addr.s_addr = inet_addr(broadcastIP);  /* Broadcast IP address */
    broadcastAddress.sin_port = htons(SENDPORT);                    /* Broadcast port. Htons converts to Big Endian - Left to Right. RTL is Little Endian */

    if (sendto(server_fd, message, messageLen, 0, (struct sockaddr *) 
           &broadcastAddress, sizeof(broadcastAddress)) != messageLen)
    {
        perror("Sendto Failure");
        exit(EXIT_FAILURE);
    }
}

int main(int argc, char *argv[])
{
    int sock;                         /* Socket */
    struct sockaddr_in broadcastAddr; /* Broadcast Address */

    queue<char *> singleQueue;

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
            char *recvString = new char[MAXRECVSTRING + 1];
            int recvStringLen;

            /* Receive a datagram from a source */
            if ((recvStringLen = recvfrom(sock, recvString, MAXRECVSTRING, MSG_DONTWAIT | MSG_PEEK, NULL, 0)) <= 0)
                break;

            recvString[recvStringLen] = '\0';

            singleQueue.push(recvString);
        }

        if(!singleQueue.empty())
        {
            char *message = singleQueue.front();
            int messageLen = strlen(message);

            if(fork() == 0)
            {
                sendMessage(message, messageLen);
                exit(EXIT_SUCCESS);
            }

            singleQueue.pop();
        }

    }
    
    close(sock);
    exit(0);
}