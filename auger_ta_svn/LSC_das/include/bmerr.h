#if !defined(_BMERR_H_)

#define _BMERR_H_ 

#define BM_OK 0

typedef enum {
  BM_CREATE_ERROR = 0x8000,
  BM_LINK_ERROR,
  BM_BAD_IDENT_ERROR,
  BM_REQUEST_NOT_FOUND,
  BM_REQUEST_TOO_OLD,   /* 8004 */
  BM_REQUEST_TOO_YOUNG, /* 8005 */
  BM_REQUEST_ALREADY,   /* 8006 */
  BM_ERROR_UNKNOWN
} BM_ERROR_TYPE ;

#endif
