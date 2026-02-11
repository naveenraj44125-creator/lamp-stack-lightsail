# Implementation Plan: AI Recommendation Display Enhancement

## Overview

This implementation plan enhances the setup script to display AI recommendations for database, bucket, and health endpoint selections. The work focuses on three main areas: extending the `select_option()` function to support database recommendations, modifying the bucket prompt to show AI recommendations, and ensuring the health endpoint prompt uses consistent yellow coloring for the AI marker.

## Tasks

- [x] 1. Extend select_option() function to support database recommendations
  - Modify the `select_option()` function in `setup/02-ui.sh`
  - Add "database" case to the recommendation_type switch statement
  - Map "database" type to `RECOMMENDED_DATABASE` variable
  - _Requirements: 6.1, 1.1, 1.5_

- [ ]* 1.1 Write property test for database marker display
  - **Property 1: Database AI Marker Display**
  - **Validates: Requirements 1.1, 1.2, 1.3, 6.2**

- [ ]* 1.2 Write unit tests for database recommendation edge cases
  - Test no marker when RECOMMENDED_DATABASE is "none"
  - Test no marker when RECOMMENDED_DATABASE is empty
  - Test invalid database type values are handled gracefully
  - _Requirements: 1.4, 6.4_

- [x] 2. Update database selection call in interactive mode
  - Modify the database selection section in `setup/08-interactive.sh`
  - Add "database" as third parameter to `select_option()` call
  - Verify the change works in interactive mode
  - _Requirements: 1.1, 1.2, 1.3_

- [ ]* 2.1 Write property test for default selection update
  - **Property 3: Default Selection Updates to AI Recommendation**
  - **Validates: Requirements 1.5, 6.3**

- [x] 3. Enhance bucket configuration prompt with AI recommendation
  - Modify the bucket configuration section in `setup/08-interactive.sh`
  - Add check for `RECOMMENDED_BUCKET` before the prompt
  - Display AI message when bucket is recommended
  - Set bucket_default based on `RECOMMENDED_BUCKET` value
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ]* 3.1 Write property test for bucket recommendation display
  - **Property 4: Bucket Recommendation Message Display**
  - **Validates: Requirements 2.1, 2.4**

- [ ]* 3.2 Write property test for bucket default value
  - **Property 5: Bucket Default Based on Recommendation**
  - **Validates: Requirements 2.2, 2.3**

- [x] 4. Fix health endpoint AI marker color consistency
  - Modify the health endpoint detection section in `setup/08-interactive.sh`
  - Change AI marker color from `${GREEN}` to `${YELLOW}`
  - Ensure consistency with other AI markers
  - _Requirements: 4.2, 4.4_

- [ ]* 4.1 Write property test for health endpoint display
  - **Property 6: Health Endpoint Detection Display**
  - **Validates: Requirements 3.1, 3.2, 3.5**

- [ ]* 4.2 Write unit tests for health endpoint edge cases
  - Test fallback behavior when RECOMMENDED_HEALTH_ENDPOINT is empty
  - Test exact endpoint path is displayed
  - Test VERIFICATION_ENDPOINT assignment on confirmation
  - _Requirements: 3.3, 3.4_

- [ ] 5. Checkpoint - Verify all AI markers display correctly
  - Run the setup script in interactive mode
  - Verify database AI marker appears when recommendation exists
  - Verify bucket AI message appears when recommendation exists
  - Verify health endpoint AI marker uses yellow color
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 6. Write visual consistency property tests
  - **Property 9: Visual Format Consistency**
  - **Property 10: AI Marker Color Consistency**
  - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [ ]* 7. Write automated mode property tests
  - **Property 11: Automated Mode Bypasses Interactive Prompts**
  - **Property 12: Environment Variables Override AI Recommendations**
  - **Property 13: AI Recommendations as Automated Mode Defaults**
  - **Property 14: Automated Mode Backward Compatibility**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**

- [ ]* 8. Write integration tests for full recommendation flow
  - Test analysis → database selection → marker display
  - Test analysis → bucket prompt → recommendation message
  - Test analysis → health endpoint → detection display
  - Test multiple recommendations working together
  - _Requirements: 1.1, 2.1, 3.1_

- [ ] 9. Final checkpoint - Run full test suite
  - Run all unit tests
  - Run all property tests (100 iterations each)
  - Run integration tests
  - Run existing automated mode test suite for backward compatibility
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The implementation maintains backward compatibility with existing automated mode configurations
- All AI markers use the `${YELLOW}` color variable for visual consistency
