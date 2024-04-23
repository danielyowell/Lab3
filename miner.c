#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/sha.h>

#define DIFFICULTY 7
#define DATA "Daniel Yowell"
#define URL "https://miners.sooners.us/latest_block.php"
#define SUBMIT_URL "https://miners.sooners.us/submit_block.php"

// Function to generate a random 10-digit number
int random_with_N_digits(int n) {
    int range_start = pow(10, n - 1);
    int range_end = pow(10, n) - 1;
    return rand() % (range_end - range_start + 1) + range_start;
}

// Function to calculate the hash value of a block
char* calculate_hash(int index, char* previous_hash, long timestamp, char* data, int nonce) {
    char block_header[1024];
    sprintf(block_header, "%d%s%ld%s%d", index, previous_hash, timestamp, data, nonce);

    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256((unsigned char*)block_header, strlen(block_header), hash);

    char* hash_str = malloc(65);
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(hash_str + (i * 2), "%02x", hash[i]);
    }
    hash_str[64] = '\0';

    return hash_str;
}

int main() {
    char* previous_hash = "[BEGIN_PROGRAM]";
    int nonce = random_with_N_digits(10);
    char prefix[8];
    memset(prefix, '0', DIFFICULTY);
    prefix[DIFFICULTY] = '\0';

    while (1) {
        // Get the latest block
        char command[1024];
        sprintf(command, "curl %s", URL);
        FILE* fp = popen(command, "r");
        if (fp == NULL) {
            printf("Failed to run command\n");
            return 1;
        }

        char response[8192];
        fread(response, 1, sizeof(response) - 1, fp);
        pclose(fp);

        // Parse the response JSON
        char* index_str = strstr(response, "\"index\":");
        int index = atoi(index_str + 9);

        char* timestamp_str = strstr(response, "\"timestamp\":");
        long timestamp = atol(timestamp_str + 13);

        char* data_str = strstr(response, "\"data\":\"") + 8;
        char* data_end = strstr(data_str, "\"");
        *data_end = '\0';

        char* hash_str = strstr(response, "\"hash\":\"") + 8;
        char* hash_end = strstr(hash_str, "\"");
        *hash_end = '\0';

        // Check if the hash has changed
        if (strcmp(hash_str, previous_hash) != 0) {
            printf("Hash change: was %s, now %s\n", previous_hash, hash_str);
            free(previous_hash);
            previous_hash = strdup(hash_str);
        }

        // Try to generate a new hash
        char* new_hash = calculate_hash(index, previous_hash, timestamp, DATA, nonce);
        if (strncmp(new_hash, prefix, DIFFICULTY) == 0) {
            printf("Nonce found: %d\n", nonce);
            printf("Block hash with %d leading zeros: %s\n", DIFFICULTY, new_hash);

            // Submit the block
            char payload[2048];
            sprintf(payload, "{\"index\":%d,\"previousHash\":\"%s\",\"timestamp\":%ld,\"data\":\"%s\",\"nonce\":%d,\"hash\":\"%s\"}",
                    index, previous_hash, time(NULL), DATA, nonce, new_hash);

            sprintf(command, "curl -X POST -H 'Content-Type: application/json' -d '%s' %s", payload, SUBMIT_URL);
            fp = popen(command, "r");
            if (fp == NULL) {
                printf("Failed to run command\n");
                return 1;
            }

            fread(response, 1, sizeof(response) - 1, fp);
            pclose(fp);

            printf("%s\n", response);
        }

        nonce++;
        free(new_hash);
    }

    free(previous_hash);
    return 0;
}