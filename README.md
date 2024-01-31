# Secure-Distributed-Computing

This is a sample program designed to demonstrate anonymous and secure salary data reporting/aggregation techniques. It is based on the salary reporting system implemented by the
Boston Women's Workforce Council. More information on this system can be found on their website: https://thebwwc.org/mpc

NOTE: This technique allows the Data Server to potentially skew the results of the survey by failing to report all the data it has collected. This can be fixed easily by adding a system where the reporting party tells the computation server how much data it is submitting. This way if there is a disparity between the data expected and the data recieved, the computation server will know that the data server has tampered with the reporting system.

## The Problem:

We want to compare average female salaries to average male salaries in a given region, or field (could be anything). We need a method for companies to report their salary data securely so that their data will remain private, but so that we can perform calculations on it.

I have solved this with a 3-party, 2-server system. The original implementation was a 2-party 1-server system in which a reporting party would submit their data to the server, and then the server would perform the calculations. The issue with this implementation is that the reporting party must trust that the server is honest because the server has access to the secret key, there is theoretically nothing stopping them from decrypting a reporting party’s submissions before aggregation, thereby violating the privacy of the reporting party. I solved this problem by separating the original server’s tasks/knowledge into two different servers. One server is responsible for key generation/distribution and data calculations, and the other server is responsible for storing encrypted data. This ensures reporter privacy because the data-server has no access to the secret key, and therefore cannot decrypt the data before aggregation, and the calculation-server has no access to the unscrambled reporter data, so while it can decrypt the data, it cannot see who submitted what data. This implementation is safe for the reporting parties barring collusion between the computation and data servers.

## Technical Description:

Computation Server:
-	Generates public/secret keypairs
-	Allows Public-Key requests via get_public_key()
-	Secret-Key is private/withheld
-	Has function to compute the averages of two lists of encrypted salaries, will return computed plaintext averages
-	Has no way to link decrypted salaries to reporting parties
Data Server:
-	Stores encrypted salary data from reporting parties
-	Shuffles salary list with each submission so that reporting party data cannot be intuited from the order of the data submissions (Not strictly necessary, but a simple added layer of security)
-	Has no access to the Secret-Key
-	Can call Computation Server function to calculate averages
Reporting Party:
-	Can request Public-Key from Computation Server
-	Uses Public-Key to encrypt employee salaries and sends lists of cyphertexts to the Data Server separated by M/F (separately submits a list of encrypted male salaries, and a list of encrypted female salaries)
