# nitrotool
Nitrotool is a frontend for [OpenSC](https://github.com/OpenSC/OpenSC) to ease
handling of the NitroKey HSM USB smart card. It might work with other smart
cards as well, I'm not certain. Basically, it is just boilerplate that does
nothing more than what is already described in the [excellent OpenSC
tutorial](https://github.com/OpenSC/OpenSC/wiki/SmartCardHSM) for the Smart
Card HSM. However, there's some annoying issues with that -- multiple tools are
needed (pkcs11-tool, pkcs15-tool, sc-hsm-tool, OpenSSL) and output formats are
sometimes not very user friendly (e.g., public keys are exported as binary DER
blobs instead of PEM files). So I wrote this little frontend to encapsulate
common tasks a bit.

## Hardware
The hardware I'm working with is the [NitroKey HSM](https://shop.nitrokey.com),
which is a quite affordable smart-card based USB HSM. I'm in no way affiliated
with them whatsoever, just think they have a pretty cool product.

## Usage
All commands have comprehensive help pages. You can get a summary of available
commands by typing:

```
$ ./nitrotool
Syntax: ./nitrotool [command] [options]

Available commands:

Options vary from command to command. To receive further info, type
    ./nitrotool [command] --help
    identify           Check if a NitroKey is connected and list all contents
    verifypin          Try to login a NitroKey by entering a PIN
    checkengine        Check if the OpenSSL engine driver works
    init               Initialize the smartcard for the first time, set default
                       SO-PIN and PIN
    explore            Explore the smartcard structure interactively
    unblock            Unblock the transponder's blocked PIN using the SO-PIN
    keygen             Create a new private keypair on the smartcard
    getkey             Fetch a public key from the smartcard
    removekey          Remove a keypair from the smartcard
    gencsr             Generate a certificate signing request from a HSM-
                       contained private key
    gencrt             Generate a self-signed certificate from a HSM-contained
                       private key

Options vary from command to command. To receive further info, type
    ./nitrotool [command] --help
```

Then, you can lookup individual help pages:

```
$ ./nitrotool keygen --help
usage: ./nitrotool keygen [--id key_id] [--label key_label] [--pin pin]
                          [--so-path path] [-v] [--help]
                          keyspec

Create a new private keypair on the smartcard

positional arguments:
  keyspec            Key specification string to generate. Can be either
                     'rsa:BITLENGTH' or 'EC:CURVENAME'. Examples are
                     'rsa:1024', 'EC:brainpool256r1' or 'EC:prime256v1'.

optional arguments:
  --id key_id        Specifies the key ID to use for generating the new key.
                     Must be an integer and defaults to 1.
  --label key_label  Specifies the key label to use for generating the new
                     key.
  --pin pin          Specifies the PIN of the smartcard. If this argument is
                     not given, the command will ask for it interactively.
  --so-path path     Search path, separated by ':' characters, in which to
                     look for shared objects like opensc-pkcs11.so. Defaults
                     to /usr/local/lib:/usr/lib:/usr/lib/x86_64-linux-gnu
  -v, --verbose      Increase verbosity. Can be specified multiple times.
  --help             Show this help page.
```

## Example
You can first query a transponder:

```
$ ./nitrotool identify
Using reader with a card: Nitrokey Nitrokey HSM (010000000000000000000000) 00 00
Version              : 2.6
Config options       :
  User PIN reset with SO-PIN enabled
SO-PIN tries left    : 15
User PIN tries left  : 3

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Default SO-PIN: 3537363231383830    Default PIN: 648219
pkcs15-tool --dump
Using reader with a card: Nitrokey Nitrokey HSM (010000000000000000000000) 00 00
PKCS#15 Card [SmartCard-HSM]:
	Version        : 0
	Serial number  : DENK#######
	Manufacturer ID: www.CardContact.de
	Flags          : 
PIN [UserPIN]
	Object Flags   : [0x3], private, modifiable
	Auth ID        : 02
	ID             : 01
	Flags          : [0x812], local, initialized, exchangeRefData
	Length         : min_len:6, max_len:15, stored_len:0
	Pad char       : 0x00
	Reference      : 129 (0x81)
	Type           : ascii-numeric
	Path           : e82b0601040181c31f0201::
	Tries left     : 3

PIN [SOPIN]
	Object Flags   : [0x1], private
	ID             : 02
	Flags          : [0x9A], local, unblock-disabled, initialized, soPin
	Length         : min_len:16, max_len:16, stored_len:0
	Pad char       : 0x00
	Reference      : 136 (0x88)
	Type           : bcd
	Path           : e82b0601040181c31f0201::
	Tries left     : 15 
```

Then, you could use it to generate a new private key:

```
$ ./nitrotool genkey EC:prime256v1 --label fookey
Using slot 0 with a present token (0x0)
Logging in to "UserPIN (SmartCard-HSM)".
Please enter User PIN: 
Key pair generated:
Private Key Object; EC
  label:      fookey
  ID:         01
  Usage:      sign, derive
Public Key Object; EC  EC_POINT 256 bits
  EC_POINT:   04410416d236f109229332666236b7af0d46d547cbb125151e1a6a657f2b2b8495b9207d40836ae3f276b55a8989385f46f16006677939b580b66636086dc3f095a4e2
  EC_PARAMS:  06082a8648ce3d030107
  label:      fookey
  ID:         01
  Usage:      verify, derive
```

Check if that worked by identifying again:

```
$ ./nitrotool id
[...]
Private EC Key [fookey]
	Object Flags   : [0x3], private, modifiable
	Usage          : [0x10C], sign, signRecover, derive
	Access Flags   : [0x1D], sensitive, alwaysSensitive, neverExtract, local
	FieldLength    : 256
	Key ref        : 1 (0x1)
	Native         : yes
	Auth ID        : 01
	ID             : 01
	MD:guid        : 7a767d92-49ec-5894-ddf2-ca7dc72ee476

Public EC Key [fookey]
	Object Flags   : [0x0]
	Usage          : [0x40], verify
	Access Flags   : [0x2], extract
	FieldLength    : 256
	Key ref        : 0 (0x0)
	Native         : no
	ID             : 01
	DirectValue    : <present>
```

Grab the public key:

```
$ ./nitrotool getpubkey --label fookey
Using slot 0 with a present token (0x0)
Logging in to "UserPIN (SmartCard-HSM)".
Please enter User PIN: 
# ECC key:
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEFtI28QkikzJmYja3rw1G1UfLsSUV
HhpqZX8rK4SVuSB9QINq4/J2tVqJiThfRvFgBmd5ObWAtmY2CG3D8JWk4g==
-----END PUBLIC KEY-----
```

Or create a CSR from a HSM key:

```
$ ./nitrotool gencsr --pin 648219
engine "pkcs11" set.
-----BEGIN CERTIFICATE REQUEST-----
MIHVMH0CAQAwGzEZMBcGA1UEAwwQTml0cm9LZXkgRXhhbXBsZTBZMBMGByqGSM49
AgEGCCqGSM49AwEHA0IABBbSNvEJIpMyZmI2t68NRtVHy7ElFR4aamV/KyuElbkg
fUCDauPydrVaiYk4X0bxYAZneTm1gLZmNghtw/CVpOKgADAKBggqhkjOPQQDAgNI
ADBFAiBybom3wRlgBDmNsm34rcOol62sgi0BHbz2PqJvwBshpgIhALdHw+PkEFeJ
pQD+3QcftVe9CZJu0uW25MEcg3S/yKOG
-----END CERTIFICATE REQUEST-----
```

## Dependencies
nitrotool itself only depends on Python3, but assumes you've installed PC/SC,
OpenSC and OpenSSL. It'll use those tools on the command line.

## License
GNU GPL-3.
